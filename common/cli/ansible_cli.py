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
from __future__ import print_function
from common.libs.ansible_executor import AnsibleExecutor
import click
from flask_cli import AppGroup

ansible_cli = AppGroup('ansible')


@ansible_cli.command('run')
@click.argument('playbooks')
@click.option('--hosts')
def run_playbook(playbooks, hosts):
    opts = {
        'private_key_file': '~/.ssh/id_rsa',
        'remote_user': 'ops',
    }
    executor = AnsibleExecutor(opts)
    result, callback = executor.run_playbook(playbooks.split(','), hosts.split(','))

    print(callback.hosts_ok)
