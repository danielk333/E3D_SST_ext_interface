#!/usr/bin/env python3


"""
"""
import time
import glob
import pathlib
import http.client
from urllib.request import pathname2url
import shutil
import os

import xmlschema

from config import SERVICES, REQUESTS
from config import HTTP_404, HTTP_200

 #TODO: fix below lines [spyne]
class SSTServer:
    '''Main external interface for handling requests to the EISCAT 3D SST Services, built to function as a :code:`wsgiref.simple_server` application.

    :param logger logger: A logger instance, all calls to the application from the simple_server will be logged to this instance.
    :param configparser.ConfigParser config: The server configuration.
    '''
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def __call__(self, env, start_response):
        try:
            try:
                ip = env['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
            except KeyError:
                ip = env['REMOTE_ADDR']

            self.logger.info(f'SSTServer: Handling request from {ip}')

            request = env['wsgi.input'].read(int(env.get('CONTENT_LENGTH', 0)))

            xml_request = etree.fromstring(request)

            request_tag = xml_request.tag
            self.logger.debug(f'SSTServer:__call__: Incoming request tag "{request_tag}"')

            if request_tag in SERVICES:
                self.logger.debug(f'SSTServer:__call__: Service "{request_tag}" executed')

                with open(SERVICES[request_tag]['schema'], 'r') as r:
                    schema_root = etree.fromstring(r.read())
                schema = etree.XMLSchema(schema_root)

                if not schema.validate(xml_request):
                    self.logger.debug(f'SSTServer:__call__:{request_tag}: Request does not match schema')
                    response = HTTP_404.encode('utf-8')
                    HTTP_RET = HTTP_404
                else:
                    self.logger.debug(f'SSTServer:__call__:{request_tag}: Request validated')
                    func = SERVICES[request_tag]['action']
                    if func is not None:
                        self.logger.debug(f'SSTServer:__call__:{request_tag}: Action executed')
                        ret_ = func(xml_request, self.config, self.logger)
                    else:
                        ret_ = None

                    response = SERVICES[request_tag]['response']
                    if response is None:
                        response = ret_.encode('utf-8')
                    else:
                        response = response.encode('utf-8')

                    if response is None:
                        response = HTTP_200.encode('utf-8')
                    HTTP_RET = HTTP_200
            else:
                response = HTTP_404.encode('utf-8')
                HTTP_RET = HTTP_404

            start_response(HTTP_RET, [
                ('Content-Type', 'text/xml'),
                ('Content-Length', str(len(response)))
            ])
        except Exception as err:
            self.logger.exception(err)

            response = HTTP_404.encode('utf-8')

            start_response(HTTP_404, [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(response)))
            ])
        self.logger.debug(f'SSTServer:__call__: Yielding response')
        yield response
