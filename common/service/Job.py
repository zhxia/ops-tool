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
import json
from common.libs.task_ctl import TaskController
from init import devops_celery
from common.models.job import Job


class JobService(object):
    @staticmethod
    def invoke_job(job_id, args, kwargs):
        job = Job.query.filter(Job.id == job_id).first()
        if not job:
            return False
        job.kwargs = json.dumps(kwargs)
        job.args = json.dumps(args)
        tc = TaskController(celery_app=devops_celery, job=job)
        result = tc.task_run()
        return result.task_id
