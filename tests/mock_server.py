# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2018, 2020 European Space Agency
# SPDX-License-Identifier: UNLICENSED

"""
Main Mock service.

A Mock server simulates a SOAP service creating a web service prototype for the test client application.

The class Mock responses to the requests checking if the type of request is valid for the service.

Main Mock server script.

It starts a Mock server on the local machine listening on the MOCK_SST_PORT through the http protocol.
It is especially used in the tests.
"""


import os
from datetime import datetime
import threading
from wsgiref.simple_server import make_server
from lxml import etree

import config_mock as cfg


class Mock:
    def __init__(self):
        self.called_n = 0

    def __call__(self, env, start_response):
        self.called_n += 1
        try:
            request = env['wsgi.input'].read(int(env.get('CONTENT_LENGTH', 0)))
            envelope = etree.fromstring(request)

            #CHECK INPUT

            response = cfg.HTTP_200.encode('utf-8')

            start_response(cfg.HTTP_200, [
                ('Content-Type', 'text/xml'),
                ('Content-Length', str(len(response)))
            ])
        except Exception as err:
            response = cfg.HTTP_404.encode('utf-8')

            start_response(cfg.HTTP_404, [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(response)))
            ])

        yield response



class TestServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = None

    def start(self, app):
        self.app = app
        self.server = make_server(self.host, self.port, app)
        self.thread = threading.Thread(target=self.server.serve_forever)

        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.server.shutdown()
            self.server.server_close()
            self.thread.join()
            del(self.server)
        self.app = None


def start_mock_server():
    mock_server = TestServer(cfg.MOCK_ESA_HOST, cfg.MOCK_ESA_PORT)
    mock_server.start(app=Mock())
    return mock_server
