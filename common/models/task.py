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


class Task(db.Model):
    __tablename__ = 'tb_task'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False, comment=u'task name')
    cls = db.Column(db.CHAR(128), unique=True, nullable=False, comment=u'task class')
    author = db.Column(db.String(64), nullable=False, default='', server_default='', comment=u'task author')
    desc = db.Column(db.String(256), nullable=False, default='', server_default='', comment='task description')
    created_at = db.Column(db.TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP(True), server_default=func.now(), onupdate=func.now())
