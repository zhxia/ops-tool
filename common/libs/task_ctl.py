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
import traceback

import celery
import redbeat
from celery.beat import ScheduleEntry
from celery.result import AsyncResult
from celery.schedules import crontab

from common.libs.str2obj import *
from common.models.job import Job


class TaskController(object):
    def __init__(self, celery_app, job):
        """
        :type celery_app: celery.Celery
        :type job: Job
        """
        self.celery_app = celery_app
        self.job = job

    def task_ctrl(self, enabled=False):
        try:
            task_key_prefix = self.celery_app.conf.get('REDBEAT_KEY_PREFIX')
            task_name = '{}{}'.format(task_key_prefix, self.job.task.cls)
            scheduler = redbeat.RedBeatSchedulerEntry.from_key(task_name, app=self.celery_app)
            scheduler.enabled = enabled
            scheduler.save()
            return True
        except Exception as e:
            traceback.print_exc()
            raise Exception(e)

    def task_run(self):
        """
        :rtype: AsyncResult
        """
        try:
            args = str_args_to_list(self.job.args)
            kwargs = str_kwargs_to_dict(self.job.kwargs)
            kwargs['task_cls'] = self.job.task.cls
            kwargs['job_id'] = self.job.id
            scheduler = redbeat.RedBeatScheduler(app=self.celery_app)
            return scheduler.send_task('scheduler.opstask.executor.TaskExecutor', args, kwargs)
        except Exception as e:
            traceback.print_exc()
            raise Exception(e)

    def task_schedule(self):
        try:
            args = str_args_to_list(self.job.args)
            kwargs = str_kwargs_to_dict(self.job.kwargs)
            kwargs['task_cls'] = self.job.task.cls
            kwargs['job_id'] = self.job.id  # 生成调度日志时需要使用
            scheduler = redbeat.RedBeatScheduler(app=self.celery_app)
            scheduler_type = self.job.scheduler_type
            if scheduler_type == 'interval':
                interval = int(self.job.schedule_expr)
                schedule = celery.schedules.schedule(run_every=interval)
            elif scheduler_type == 'cron':
                cron_arr = self.job.schedule_expr.split(' ')
                schedule = crontab(minute=cron_arr[0], hour=cron_arr[1], day_of_month=cron_arr[2],
                                   month_of_year=cron_arr[3], day_of_week=cron_arr[4], app=self.celery_app)
            else:
                return
            s = scheduler.add(**{
                'name': self.job.task.cls,
                'task': 'scheduler.opstask.executor.TaskExecutor',
                'schedule': schedule,
                'args': args,
                'kwargs': kwargs,
                'enabled': False if self.job.enabled == 0 else True
            })  # type: ScheduleEntry
            # s.enabled = False
            s.save()
            return s.reschedule()
        except Exception as e:
            traceback.print_exc()
            raise Exception(e)
