#!/usr/bin/env python3


"""
"""
import time
import glob
import pathlib
import http.client

from lxml import etree

import services 
from config import config

HTTP_200 = '200 OK'
HTTP_404 = '404 Not Found'

SERVICES = {
    'SubmitObservationDataRequestType': services.simulate_measurements,
}

inbox = config.get('SST Client', 'Inbox')
if inbox.startswith('.'):
    if len(inbox) > 1:
        inbox = pathlib.Path(__file__).parent / inbox[1:]
    else:
        inbox = pathlib.Path(__file__).parent
else:
    inbox = pathlib.Path(inbox)

archive = config.get('SST Client', 'Archive')
if archive.startswith('.'):
    if len(archive) > 1:
        archive = pathlib.Path(__file__).parent / archive[1:]
    else:
        archive = pathlib.Path(__file__).parent
else:
    archive = pathlib.Path(archive)

file_ext = config.get('SST Client', 'File-extensions').split(',')
file_ext = [x.strip() for x in file_ext]


class SSTClient:

    def __init__(self, logger):
        self.logger = logger


    def run(self):
        self.logger.info('SST Client: STARTED')
        self.__run = True
        while self.__run:
            self.logger.debug('SST Client: looking for new tracklets to deliver')

            files = []
            for ext in file_ext:
                files += inbox.glob('**/*.{ext}')

            self.logger.info(f'SST Client: {len(files)} files found, delivering')

            rest = http.client.HTTPConnection(
                config.get('SST Client', 'Deliver Server'), 
                config.getint('SST Client', 'Deliver Port'),
            )

            for file in files:
                data = open(file, 'r').read().encode("UTF-8")
                header = {
                    'Content-Type': 'text/xml',
                    'Content-Length': str(len(data)),
                }

                rest.request('POST', config.get('SST Client', 'Deliver Path'), body=data, headers=header)
            
                response = rest.getresponse()
                raw = response.read().decode("utf-8")
                self.logger.debug(f'SST Client: Delivery response {raw}')

            time.sleep(config.getfloat('SST Client', 'Deliver interval'))


    def stop(self):
        self.__run = False
        self.logger.info('SST Client: STOPPED')



class SSTApplication:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, env, start_response):
        try:
            request = env['wsgi.input'].read(int(env.get('CONTENT_LENGTH', 0)))

            schema_root = etree.XML('templates/commonSSTDataModel/esa/ssa/sst/common/planning/planning.xsd')
            schema = etree.XMLSchema(schema_root)
            parser = etree.XMLParser(schema = schema)

            xml_request = etree.fromstring(request, parser)
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
