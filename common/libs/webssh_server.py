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

import logging

import tornado.ioloop
import tornado.web
from tornado.options import options
from webssh import handler
from webssh.handler import IndexHandler, WsockHandler, NotFoundHandler
from webssh.settings import (
    get_app_settings, get_host_keys_settings, get_policy_setting,
    get_ssl_context, get_server_settings, check_encoding_setting
)


class IndexHandler(IndexHandler):
    def check_xsrf_cookie(self):
        return True


class WsockHandler(WsockHandler):
    def check_xsrf_cookie(self):
        return True

    def check_origin(self, origin):
        return True


class WebSSHServer(object):
    def run(self, args=[]):
        # args = ['--logging=debug']
        args.insert(0, '')
        options.parse_command_line(args=args)
        print options.as_dict()
        check_encoding_setting(options.encoding)
        loop = tornado.ioloop.IOLoop.current()
        app = self.make_app(self.make_handlers(loop, options), get_app_settings(options))
        ssl_ctx = get_ssl_context(options)
        server_settings = get_server_settings(options)
        self.app_listen(app, options.port, options.address, server_settings)
        if ssl_ctx:
            server_settings.update(ssl_options=ssl_ctx)
            self.app_listen(app, options.sslport, options.ssladdress, server_settings)
        loop.start()

    @staticmethod
    def make_handlers(loop, opts):
        host_keys_settings = get_host_keys_settings(opts)
        policy = get_policy_setting(opts, host_keys_settings)

        handlers = [
            (r'/', IndexHandler, dict(loop=loop, policy=policy,
                                      host_keys_settings=host_keys_settings)),
            (r'/ws', WsockHandler, dict(loop=loop))
        ]
        return handlers

    @staticmethod
    def make_app(handlers, settings):
        settings.update(default_handler_class=NotFoundHandler)
        return tornado.web.Application(handlers, **settings)

    @staticmethod
    def app_listen(app, port, address, server_settings):
        app.listen(port, address, **server_settings)
        if not server_settings.get('ssl_options'):
            server_type = 'http'
        else:
            server_type = 'https'
            handler.redirecting = True if options.redirect else False
        logging.info(
            'Listening on {}:{} ({})'.format(address, port, server_type)
        )
