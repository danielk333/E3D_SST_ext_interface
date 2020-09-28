#!/usr/bin/env python3


"""
"""
import time

from lxml import etree

import services 

HTTP_200 = '200 OK'
HTTP_404 = '404 Not Found'

SERVICES = {
    'SubmitObservationDataRequestType': services.simulate_measurements,
}


class SSTClient:

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

            xml_request = etree.fromstring(request)
            request_tag = xml_request.tag.split('}')[-1]
            self.logger.debug(f'SSTApplication:__call__: Incoming request tag "{request_tag}"')

            if request_tag in SERVICES:
                self.logger.debug(f'SSTApplication:__call__: Service "{request_tag}" executed')
                func = SERVICES[request_tag]
                response = func(xml_request).encode('utf-8')
            else:
                response = HTTP_404.encode('utf-8')

            start_response(HTTP_404, [
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
