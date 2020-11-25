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

import redbeat
from flask_cli import AppGroup
from flask_cli import with_appcontext
from celery.bin import beat, worker
from scheduler.opstask import *

celery_cli = AppGroup('celery')


@celery_cli.command('worker')
@with_appcontext
def run_worker():
    sworker = worker.worker(app=app.devops_celery)
    options = {
        'loglevel': 'INFO',
        'traceback': True
    }
    return sworker.run(**options)


@celery_cli.command('beat')
@with_appcontext
def run_beat():
    sbeat = beat.beat(app=app.devops_celery)
    options = {
        'max_interval': 60,
        'loglevel': 'DEBUG',
        'scheduler': redbeat.RedBeatScheduler,
    }
    return sbeat.run(**options)
