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

import importlib
# import os
import time

from celery import states
from celery.signals import task_prerun

from common.models.job import Job
from common.models.job_log import JobLog
from init import app, db

# path = '{cwd}/../tasks/'.format(cwd=os.path.dirname(os.path.abspath(__file__)))
# task_list = next(os.walk(path))[1]
# for t in task_list:
#     if t.startswith('_'):
#         continue
#     task_module = importlib.import_module('scheduler.tasks.{}'.format(t))
#     task_cls = getattr(task_module, 'JobTask')
#     task = app.devops_celery.register_task(task_cls())
#     print 'task added:', task
#     print 'tasks:', app.devops_celery.tasks

task_module = importlib.import_module('scheduler.opstask.executor')
task_cls = getattr(task_module, 'TaskExecutor')
task = app.devops_celery.register_task(task_cls())


def task_add_log(sender=None, task_id=None, *args, **kwargs):
    # print('sender:', sender)
    # print('#######', sender.__module__)
    # this line intercept sys task
    if sender.__module__ == 'scheduler.tasks.bootstrap':
        return
        # print('args:', args)
    # print('kwargs:', kwargs)
    job_kwargs = kwargs.get('kwargs')
    job_id = job_kwargs.get('job_id')
    job = Job.query.filter(Job.id == job_id).first()
    if not job:
        print('job:{} not found!'.format(job_id))
        return
    job_log = JobLog.query.filter(JobLog.job_run_id == task_id).first()
    if not job_log:
        job_log = JobLog()
    with db.auto_rollback():
        job_log.job_id = job_id
        job_log.job_run_id = task_id
        job_log.started_at = int(time.time())
        job_log.status = states.STARTED
        db.session.add(job_log)


task_prerun.connect(task_add_log)
