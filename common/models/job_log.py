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
from sqlalchemy import func
from init import db


class JobLog(db.Model):
    __tablename__ = 'tb_job_log'
    id = db.Column(db.BIGINT(), primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer(), db.ForeignKey('tb_job.id'), comment='job id')
    job_run_id = db.Column(db.String(64), nullable=False, default='', server_default='', comment=u'job执行id')
    retry_count = db.Column(db.Integer, default='0', nullable=False, server_default='0', comment=u'重试次数')
    started_at = db.Column(db.INT(), default='0', server_default='0', comment=u'job开始时间')
    finished_at = db.Column(db.INT(), default='0', server_default='0', comment=u'job结束时间')
    status = db.Column(
        db.Enum('PENDING', 'RECEIVED', 'STARTED', 'SUCCESS', 'FAILURE', 'REVOKED', 'REJECTED', 'RETRY', 'IGNORED'),
        comment=u'job状态')
    detail = db.Column(db.Text, default='', server_default='', comment=u'job执行详细')
    created_at = db.Column(db.TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP(True), server_default=func.now(), onupdate=func.now())
