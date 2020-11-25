# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import logging
import os
from tempfile import NamedTemporaryFile

import jinja2
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager

from ansible import context


class ResultCollector(CallbackBase):
    def __init__(self, display=None, options=None):
        super(ResultCollector, self).__init__(display, options)
        self.hosts_ok = []
        self.hosts_failed = []
        self.hosts_unreachable = []

    def v2_runner_on_failed(self, result, ignore_errors=False):
        super(ResultCollector, self).v2_runner_on_failed(result, ignore_errors)
        task = result._task.get_name()
        host = result._host.get_name()
        self.hosts_failed.append({'task': task, 'host': host, 'result': result._result})

    def v2_runner_on_ok(self, result):
        super(ResultCollector, self).v2_runner_on_ok(result)
        task = result._task.get_name()
        host = result._host.get_name()
        self.hosts_ok.append({'task': task, 'host': host, 'result': result._result})

    def v2_runner_on_unreachable(self, result):
        super(ResultCollector, self).v2_runner_on_unreachable(result)
        task = result._task.get_name()
        host = result._host.get_name()
        self.hosts_unreachable.append({'task': task, 'host': host, 'result': result._result})


class AnsibleExecutor(object):
    def __init__(self, opts):
        self._options = opts

    def run_playbook(self, playbooks, hosts=[]):
        hosts = hosts if hosts else self._options.get('hosts')
        playbooks = playbooks if playbooks else self._options.get('playbooks')
        remote_user = self._options.get('remote_user', 'ops')
        private_key_file = self._options.get('private_key_file')
        loader = DataLoader()
        context.CLIARGS = ImmutableDict(
            tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
            module_path=None, forks=10, remote_user=remote_user, private_key_file=private_key_file,
            ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=None,
            become_method=None, become_user=None, verbosity=True, check=False, start_at_task=None
        )
        inventory_tpl = """
                [nodes]
                {% for host in hosts%}
                {{host}}
                {%endfor%}
                """
        inventory_content = jinja2.Template(inventory_tpl).render({'hosts': hosts})
        tmp_dir = '/tmp/ansible/'
        try:
            if not os.path.exists(tmp_dir):
                os.mkdir(tmp_dir)
        except Exception as e:
            logging.info('create tmp dir:"{}" failed,change to:"/tmp/",error:{}'.format(tmp_dir, e.__str__()))
            tmp_dir = '/tmp/'

        source = NamedTemporaryFile(delete=False, suffix='.tmp', dir=tmp_dir)
        source.write(inventory_content.encode('utf-8'))
        source.close()
        inventory_manager = InventoryManager(loader=loader, sources=source.name)
        variable_manager = VariableManager(loader=loader, inventory=inventory_manager)
        playbook_executor = PlaybookExecutor(
            playbooks=playbooks,
            inventory=inventory_manager,
            loader=loader,
            variable_manager=variable_manager,
            passwords={}
        )
        result_callback = ResultCollector()
        playbook_executor._tqm._stdout_callback = result_callback
        try:
            result = playbook_executor.run()
            return result, result_callback
        finally:
            os.remove(source.name)
