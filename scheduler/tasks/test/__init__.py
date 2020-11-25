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
from scheduler.base_task import BaseTask


class JobTask(BaseTask):

    def task_info(self):
        return {
            'name': u'测试任务',
            'desc': u'仅用于测试，勿用于生产环境',
            'author': u'zhxia',
        }

    def run(self, *args, **kwargs):
        return {'code': 0, 'data': 'success', 'msg': 'ok'}
