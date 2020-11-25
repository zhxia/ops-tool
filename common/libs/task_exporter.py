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
import os
import sys


class TaskExporter(object):
    def scan(self, d=None):
        task_modules = []
        if not d:
            d = '{}/scheduler/tasks'.format(os.getcwd())
        try:
            module_list = next(os.walk(d))[1]
            for module in module_list:
                if module.startswith('_'):
                    continue
                nd = '{}/{}'.format(d, module)
                r = nd.rsplit('scheduler/')
                t = 'scheduler.{}'.format(r[1].replace('/', '.'))
                # push real task to list
                task_modules.append(t)
                task_modules.extend(self.scan(nd))
        except StopIteration:
            pass

        return task_modules

    def export(self):
        modules = self.scan()
        task_list = []
        for module in modules:
            if module in sys.modules:
                sys.modules.pop(module)
            mod = importlib.import_module(module)
            if not hasattr(mod, 'JobTask'):
                continue
            task_cls = getattr(mod, 'JobTask')
            task_list.append(task_cls())
        return task_list
