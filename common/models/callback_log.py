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
from sqlalchemy.sql import func
from init import db


class CallbackLog(db.Model):
    __tablename__ = 'tb_callback_log'
    id = db.Column(db.BIGINT, autoincrement=True, primary_key=True)
    callback_id = db.Column(db.String(64), nullable=False, default='', server_default='', comment=u'job执行id')
    callback_url = db.Column(db.String(128), nullable=False, default='', server_default='', comment=u'回调url')
    response = db.Column(db.String(512), nullable=False, default='', server_default='', comment=u'回调响应')
    created_at = db.Column(db.TIMESTAMP(True), server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP(True), server_default=func.now(), onupdate=func.now())
