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
from sqlalchemy.sql import expression

from init import db
from task import Task


class Job(db.Model):
    __tablename__ = 'tb_job'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer(), db.ForeignKey('tb_task.id'), comment='task id')
    name = db.Column(db.String(256), nullable=False, comment=u'job name')
    schedule_expr = db.Column(db.String(64), default='', server_default='', comment=u'调度表达式')
    scheduler_type = db.Column(db.Enum('cron', 'interval', 'manual'), default='manual', server_default='manual',
                               comment=u'调度类型')
    args = db.Column(db.String(256), nullable=False, default='', server_default='', comment=u'列表参数')
    kwargs = db.Column(db.String(256), nullable=False, default='', server_default='', comment=u'字典列表')
    owner = db.Column(db.String(64), nullable=False, default='', server_default='', comment=u'任务负责人')
    enabled = db.Column(db.BOOLEAN, default=expression.true(), nullable=False)
    notify_url = db.Column(db.String(128), default='', server_default='', comment=u'任务回调URL')
    alarm_type = db.Column(db.Enum('email', 'sms', 'wework', 'wechat', 'dingding', 'phone'), default='email',
                           server_default='email', comment=u'失败告警方式')
    alarm_target = db.Column(db.String(256), default='', server_default='', comment=u'告警对象')
    created_at = db.Column(db.TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP(True), server_default=func.now(), onupdate=func.now())
    task = db.relationship('task.Task')  # type: Task
