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
import os
from celery.schedules import crontab
from kombu import Queue, Exchange
from . import CeleryConfig


class CeleryConfigDevelopment(CeleryConfig):
    BROKER_URL = 'redis://127.0.0.1/1'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1/2'
    CELERY_TASK_RESULT_EXPIRES = 3600
    CELERYD_MAX_TASKS_PER_CHILD = 128
    REDBEAT_KEY_PREFIX = 'redbeat:'
    CELERY_IMPORTS = (
        'scheduler.tasks.bootstrap',
    )
    CELERY_DEFAULT_QUEUE = 'default'
    CELERY_DEFAULT_EXCHANGE = 'default'
    CELERY_DEFAULT_ROUTING_KEY = 'default'
    CELERY_QUEUES = (
        Queue('default', Exchange('default', type='direct'), routing_key='default'),
        Queue('sys', Exchange('sys', type='direct'), routing_key='sys'),
        Queue('high_priority', Exchange('high_priority', type='direct'), routing_key='high_priority'),
    )
    CELERY_ROUTES = {
        'scheduler.tasks.bootstrap.*': {'queue': 'sys', 'routing_key': 'sys'},
    }

    CELERYBEAT_SCHEDULE = {
        'auto_task_scan': {
            'task': 'scheduler.tasks.bootstrap.task_scan',
            'schedule': crontab(minute='*/1'),
            'args': ()
        },
    }
    ONCE = {
        'backend': 'celery_once.backends.Redis',
        'settings': {
            'url': 'redis://127.0.0.1:6379/3',
            'default_timeout': 60 * 60
        }
    }


env = os.getenv('FLASK_ENV', 'Production').capitalize()
celery_cfg = globals()['CeleryConfig{}'.format(env)]
