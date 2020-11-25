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
import traceback

import click
import redbeat
from celery.utils.imports import gen_task_name
from flask_cli import AppGroup

from common.libs.str2obj import str_args_to_list, str_kwargs_to_dict
from common.libs.task_ctl import TaskController
from common.libs.task_exporter import TaskExporter
from common.models.job import Job
from init import app, db

task_cli = AppGroup('task')


@task_cli.command('scan')
def task_scan():
    task_exporter = TaskExporter()
    tasks = task_exporter.export()
    for task in tasks:
        task_cls = gen_task_name(app.devops_celery, task.__name__, task.__module__)
        task_info = task.task_info()  # type:dict
        task_name = task_info.get('name', task_cls)
        task_desc = task_info.get('desc', '')
        task_author = task_info.get('author', 'anonymous')
        job = Job.query.filter(Job.cls == task_cls).first()
        if not job:
            job = Job()
        with db.auto_rollback():
            job.name = task_name
            job.desc = task_desc
            job.cls = task_cls
            job.author = task_author
            db.session.add(job)


@task_cli.command("run")
@click.argument("task_name")
@click.option("--args", default='')
@click.option('--kwargs', default='')
def run_job(task_name, args, kwargs):
    module = importlib.import_module('scheduler.tasks.{task}'.format(task=task_name))
    cls = getattr(module, 'JobTask')
    try:
        args = str_args_to_list(args)
        kwargs = str_kwargs_to_dict(kwargs)
        ret = cls().run(*args, **kwargs)
        return ret
    except Exception as e:
        traceback.print_exc()
        raise Exception(e)


@task_cli.command('del')
@click.argument('task_name')
def job_scheduler_delete(task_name):
    task_key_prefix = app.devops_celery.conf.get('REDBEAT_KEY_PREFIX')
    task_name = '{}{}'.format(task_key_prefix, task_name)
    entity = redbeat.RedBeatSchedulerEntry.from_key(task_name, app=app.devops_celery)
    entity.delete()


@task_cli.command('run')
@click.argument('job_id')
def job_scheduler_add(job_id):
    try:
        job = Job.query.filter(Job.id == job_id).first()  # type: Job
        if not job:
            print('job not found:{}'.format(job_id))
            return
        tcl = TaskController(app.devops_celery, job)
        res = tcl.task_run()
        print(res.get(1))
    except Exception as e:
        traceback.print_exc()
        raise Exception(e)


@task_cli.command('add')
@click.argument('job_id')
def job_scheduler_add(job_id):
    try:
        job = Job.query.filter(Job.id == job_id).first()  # type: Job
        if not job:
            print('job not found:{}'.format(job_id))
            return
        tcl = TaskController(app.devops_celery, job)
        res = tcl.task_schedule()
        print(res)
    except Exception as e:
        traceback.print_exc()
        raise Exception(e)


@task_cli.command('ctl')
@click.argument('task_name')
@click.argument('enabled')
def job_control(task_name, enabled):
    try:
        task_key_prefix = app.devops_celery.conf.get('REDBEAT_KEY_PREFIX')
        task_name = '{}{}'.format(task_key_prefix, task_name)
        scheduler = redbeat.RedBeatSchedulerEntry.from_key(task_name, app=app.devops_celery)
        scheduler.enabled = True if enabled == 'true' else False
        scheduler.save()
    except Exception as e:
        traceback.print_exc()
        raise Exception(e)
