#!/usr/bin/env python3


"""
"""
import time
import glob
import pathlib
import http.client
import shutil

from lxml import etree

from config import SERVICES, REQUESTS
from config import HTTP_404, HTTP_200


class SSTClient:

    def __init__(self, config, logger, delivery_log=False):
        self.logger = logger
        self.config = config
        self.delivery_log = delivery_log
        self.deliveries = []

        inbox = config.get('SST Client', 'Inbox')
        if inbox.startswith('.'):
            if len(inbox) > 1:
                inbox = pathlib.Path(__file__).parent / inbox[1:]
            else:
                inbox = pathlib.Path(__file__).parent
        else:
            inbox = pathlib.Path(inbox)

        self.inbox = inbox

        archive = self.config.get('SST Client', 'Archive')
        if archive.startswith('.'):
            if len(archive) > 1:
                archive = pathlib.Path(__file__).parent / archive[1:]
            else:
                archive = pathlib.Path(__file__).parent
        else:
            archive = pathlib.Path(archive)

        self.archive = archive

        self.file_ext = self.config.get('SST Client', 'File-extensions').split(',')
        self.file_ext = [x.strip() for x in self.file_ext]



    def run(self):
        self.logger.info('SST Client: STARTED')
        self.__run = True

        schema_root = etree.XML(REQUESTS['TDM']['schema'])
        schema = etree.XMLSchema(schema_root)

        while self.__run:
            self.logger.debug('SST Client: looking for new tracklets to deliver')

            files = []
            for ext in self.file_ext:
                files += self.inbox.glob('**/*.{ext}')

            files = [pathlib.Path(file) for file in files]

            self.logger.info(f'SST Client: {len(files)} files found, delivering')

            rest = http.client.HTTPConnection(
                self.config.get('SST Client', 'Deliver Server'), 
                self.config.getint('SST Client', 'Deliver Port'),
            )

            for file in files:
                tdm_xml = etree.parse(open(file, 'r'))

                if not schema.validate(tdm_xml):
                    self.logger.debug(f'SST Client: file "{file}" not valid TDM-XML')
                    continue

                data = tdm_xml.tostring().encode("UTF-8")
                header = {
                    'Content-Type': 'text/xml',
                    'Content-Length': str(len(data)),
                }

                rest.request('POST', REQUESTS['TDM']['path'], body=data, headers=header)
            
                response = rest.getresponse()
                raw = response.read().decode("utf-8")
                
                if raw == REQUESTS['TDM']['response']:
                    shutil.move(file, self.archive / file.name)
                    self.logger.debug(f'SST Client: Delivery completed')
                    if self.delivery_log:
                        self.deliveries += [file]
                else:
                    self.logger.debug(f'SST Client: Delivery failed "{raw}"')

            time.sleep(self.config.getfloat('SST Client', 'Deliver interval'))


    def stop(self):
        self.__run = False
        self.logger.info('SST Client: STOPPED')



class SSTServer:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def __call__(self, env, start_response):
        try:
            request = env['wsgi.input'].read(int(env.get('CONTENT_LENGTH', 0)))

            xml_request = etree.fromstring(request)

            request_tag = xml_request.tag
            self.logger.debug(f'SSTServer:__call__: Incoming request tag "{request_tag}"')

            if request_tag in SERVICES:
                self.logger.debug(f'SSTServer:__call__: Service "{request_tag}" executed')

                schema_root = etree.XML(SERVICES[request_tag]['schema'])
                schema = etree.XMLSchema(schema_root)
                schema.validate(xml_request)
                
                func = SERVICES[request_tag]['action']
                if func is not None:
                    ret_ = func(xml_request, self.config)
                else:
                    ret_ = None

                 response = SERVICES[request_tag]['response']
                 if response is None:
                    response = ret_
                if response is None:
                    response = HTTP_200.encode('utf-8')

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
