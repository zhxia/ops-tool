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
from celery.utils.imports import gen_task_name
from celery.utils.log import get_task_logger
from celery_once import QueueOnce
from celery import states
from common.libs.task_exporter import TaskExporter
from common.models.task import Task
from init import devops_celery as celery_app, db

logger = get_task_logger(__name__)


@celery_app.task(base=QueueOnce, once={'graceful': True})
def task_scan():
    logger.info('auto task scan...')
    task_exporter = TaskExporter()
    tasks = task_exporter.export()
    for task in tasks:
        task_cls = gen_task_name(celery_app, task.__name__, task.__module__)
        task_info = task.task_info()  # type:dict
        task_name = task_info.get('name', task_cls)
        task_desc = task_info.get('desc', '')
        task_author = task_info.get('author', 'anonymous')
        task = Task.query.filter(Task.cls == task_cls).first()
        if not task:
            task = Task()
        with db.auto_rollback():
            task.name = task_name
            task.desc = task_desc
            task.cls = task_cls
            task.author = task_author
            db.session.add(task)
    logger.info('auto task scan finished!')


@celery_app.task()
def task_callback(*args, **kwargs):
    url = kwargs.get('callback_url')
    job_run_id = kwargs.get('job_run_id')
    result = kwargs.get('result')
    state = kwargs.get('state')
    req_data = {
        'job_run_id': job_run_id,
        'result': result,
        'state': state
    }
    return req_data
