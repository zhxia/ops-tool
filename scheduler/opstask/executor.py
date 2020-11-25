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
import importlib
import traceback
import sys

from scheduler.base_task import BaseTask


class TaskExecutor(BaseTask):
    """
    所有task入口
    """

    def run(self, *args, **kwargs):
        task_cls = kwargs.get('task_cls')
        return self.run_task(task_cls, *args, **kwargs)

    def run_task(self, task_cls_name, *args, **kwargs):
        # type: (str, set, dict) -> object
        base_package = 'scheduler.tasks.'
        cls_name = '.JobTask'
        task_name = task_cls_name.replace(base_package, '').replace(cls_name, '')
        task_name = task_name.lstrip()
        module_name = 'scheduler.tasks.{task_name}'.format(task_name=task_name)
        # refresh loaded module
        if module_name in sys.modules:
            sys.modules.pop(module_name)
        module = importlib.import_module(module_name)
        cls = getattr(module, 'JobTask')
        try:
            ret = cls().run(*args, **kwargs)
            return ret
        except Exception as e:
            traceback.print_exc()
            raise self.retry(exc=e)
