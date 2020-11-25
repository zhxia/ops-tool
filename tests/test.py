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


def test_task_run():
    from init import devops_celery
    from celery.result import AsyncResult
    result = devops_celery.send_task('scheduler.opstask.executor.TaskExecutor', ['aliyun'])  # type: AsyncResult
    print result, result.get(0.5)


def test_tool():
    import os
    from celery.utils.imports import gen_task_name
    from init import devops_celery
    os.chdir('../')
    from common.libs.task_exporter import TaskExporter
    te = TaskExporter()
    for task in te.export():
        print gen_task_name(devops_celery, task.__name__, task.__module__)


def test_split():
    str1 = '/Users/zhxia/workspace/python/autoops/scheduler/tasks/aliyun/slb_test'
    r = str1.rsplit("scheduler/")
    print 'aa', 'scheduler.{}'.format(r[1].replace('/', '.'))


def test_db():
    from init import db
    print db

    base_package = 'scheduler.tasks.'
    task_name = 'scheduler.tasks.test.JobTask'
    print task_name.replace(base_package, '').replace('.JobTask', '')


def test_show():
    def aa(*args, **kwargs):
        print args, kwargs

    aa('aa', *['bb', 'cc'], **{'d': 1, 'e': 2})
