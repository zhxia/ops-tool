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
from flask_cors import CORS
from celery import Celery
from flask import Flask
from common.libs.dbbase import SQLAlchemy
from config.app_config import app_cfg
from config.celery_config import celery_cfg


def make_celery(flask_app):
    """

    :type flask_app: Flask
    """
    celery_app = Celery(app.import_name)
    celery_app.config_from_object(celery_cfg)
    celery_app.conf.enable_utc = True

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app


app = Flask(__name__)
app.config.from_object(app_cfg)
devops_celery = make_celery(app)
db = SQLAlchemy()
db.init_app(app)
setattr(app, 'devops_celery', devops_celery)
CORS(supports_credentials=True).init_app(app)
