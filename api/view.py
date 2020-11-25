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
from celery.result import AsyncResult
from flask import request

from common.service.Job import JobService
from init import app, devops_celery


@app.route('/job/submit', endpoint='job_submit', methods=['POST'])
def job_submit():
    params = request.get_json()
    job_id = params.get('job_id')
    try:
        job_run_id = JobService.invoke_job(job_id, params.get('args'), params.get('kwargs'))
        return {'code': 0, 'data': {'job_run_id': job_run_id}, 'message': 'success'}
    except Exception as e:
        return {'code': 0, 'data': None, 'message': e.__str__()}


@app.route('/job/result/<job_run_id>', endpoint='job_result', methods=['GET'])
def job_result(job_run_id):
    result = AsyncResult(id=job_run_id, app=devops_celery)
    try:
        res = result.get(2)
        return {'code': 0, 'data': res, 'message': 'success'}
    except Exception as e:
        return {'code': -1, 'data': None, 'message': e.__str__()}
