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
import celery
import json
from celery import states
import time
import redbeat
from init import db
from common.models.job_log import JobLog


class BaseTask(celery.Task):
    def task_info(self):
        return {}

    def run(self, *args, **kwargs):
        raise NotImplementedError('not implement')

    def on_success(self, retval, task_id, args, kwargs):
        """Success handler.

                Run by the worker if the task executes successfully.

                Arguments:
                    retval (Any): The return value of the task.
                    task_id (str): Unique id of the executed task.
                    args (Tuple): Original arguments for the executed task.
                    kwargs (Dict): Original keyword arguments for the executed task.

                Returns:
                    None: The return value of this handler is ignored.
                """
        job_log = JobLog.query.filter(JobLog.job_run_id == task_id).first()  # type:JobLog
        if job_log:
            with db.auto_rollback():
                detail = {'input': {'args': args, 'kwargs': kwargs}, 'output': retval}
                job_log.detail = json.dumps(detail)
                job_log.status = states.SUCCESS
                job_log.finished_at = int(time.time())
                db.session.add(job_log)
        callback_url = kwargs.get('callback_url')
        if callback_url is None:
            return
        scheduler = redbeat.RedBeatScheduler(app=self.app)
        scheduler.send_task('scheduler.tasks.bootstrap.task_callback', [],
                            {'job_run_id': task_id, 'callback_url': callback_url, 'state': states.SUCCESS,
                             'result': retval})
        super(BaseTask, self).on_success(retval, task_id, args, kwargs)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry handler.

                This is run by the worker when the task is to be retried.

                Arguments:
                    exc (Exception): The exception sent to :meth:`retry`.
                    task_id (str): Unique id of the retried task.
                    args (Tuple): Original arguments for the retried task.
                    kwargs (Dict): Original keyword arguments for the retried task.
                    einfo (~billiard.einfo.ExceptionInfo): Exception information.

                Returns:
                    None: The return value of this handler is ignored.
                """
        job_log = JobLog.query.filter(JobLog.job_run_id == task_id).first()  # type:JobLog
        if job_log:
            with db.auto_rollback():
                detail = {'input': {'args': args, 'kwargs': kwargs}, 'output': exc.__str__()}
                job_log.retry_count += 1
                job_log.status = states.RETRY
                job_log.detail = detail
                db.session.add(job_log)
        super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Error handler.

                This is run by the worker when the task fails.

                Arguments:
                    exc (Exception): The exception raised by the task.
                    task_id (str): Unique id of the failed task.
                    args (Tuple): Original arguments for the task that failed.
                    kwargs (Dict): Original keyword arguments for the task that failed.
                    einfo (~billiard.einfo.ExceptionInfo): Exception information.

                Returns:
                    None: The return value of this handler is ignored.
                """
        job_log = JobLog.query.filter(JobLog.job_run_id == task_id).first()  # type:JobLog
        if job_log:
            with db.auto_rollback():
                detail = {'input': {'args': args, 'kwargs': kwargs}, 'output': exc.__str__()}
                job_log.detail = json.dumps(detail)
                job_log.status = states.FAILURE
                job_log.finished_at = int(time.time())
                db.session.add(job_log)
        callback_url = kwargs.get('callback_url')
        if callback_url is None:
            return
        scheduler = redbeat.RedBeatScheduler(app=self.app)
        scheduler.send_task('scheduler.tasks.bootstrap.task_callback', [],
                            {'job_run_id': task_id, 'callback_url': callback_url, 'state': states.FAILURE,
                             'result': exc.__str__()})
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Handler called after the task returns.

                Arguments:
                    status (str): Current task state.
                    retval (Any): Task return value/exception.
                    task_id (str): Unique id of the task.
                    args (Tuple): Original arguments for the task.
                    kwargs (Dict): Original keyword arguments for the task.
                    einfo (~billiard.einfo.ExceptionInfo): Exception information.

                Returns:
                    None: The return value of this handler is ignored.
                """
        super(BaseTask, self).after_return(status, retval, task_id, args, kwargs, einfo)
