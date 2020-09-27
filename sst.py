#!/usr/bin/env python3


"""
"""
import time

from lxml import etree

HTTP_200 = '200 OK'
HTTP_404 = '404 Not Found'

class TrackletSender:

    def __init__(self, logger):
        self.logger = logger


    def run(self):
        self.logger.info('SST Client: STARTED')
        self.__run = True
        while self.__run:
            time.sleep(1)
            self.logger.info('SST Client: executing?')
            pass

    def stop(self):
        self.__run = False
        self.logger.info('SST Client: STOPPED')



class SSTApplication:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, env, start_response):
        try:
            request = env['wsgi.input'].read(int(env.get('CONTENT_LENGTH', 0)))
            response = HTTP_200.encode('utf-8')

            start_response(HTTP_200, [
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

        yield response
