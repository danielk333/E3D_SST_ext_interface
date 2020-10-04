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

from lxml import etree

from config import SERVICES, REQUESTS
from config import HTTP_404, HTTP_200

##Scruffed from https://stackoverflow.com/a/55616129
##
# The XML_CATALOG_FILES environment variable is used by libxml2 (which is used by lxml).
# See http://xmlsoft.org/catalog.html.
if "XML_CATALOG_FILES" not in os.environ:
    # Path to catalog must be a url.
    catalog_path = f"file:{pathname2url(os.path.join(os.getcwd(), 'catalog.xml'))}"
    # Temporarily set the environment variable.
    os.environ['XML_CATALOG_FILES'] = catalog_path


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
        self.logger.debug(f'SST Client: inbox={self.inbox}')

        archive = self.config.get('SST Client', 'Archive')
        if archive.startswith('.'):
            if len(archive) > 1:
                archive = pathlib.Path(__file__).parent / archive[1:]
            else:
                archive = pathlib.Path(__file__).parent
        else:
            archive = pathlib.Path(archive)

        self.archive = archive
        self.logger.debug(f'SST Client: archive={self.archive}')

        self.file_ext = self.config.get('SST Client', 'File-extensions').split(',')
        self.file_ext = [x.strip() for x in self.file_ext]
        self.logger.debug(f'SST Client: file extensions={self.file_ext}')



    def run(self):
        self.logger.info('SST Client: STARTED')
        self.__run = True

        #with open(REQUESTS['TDM']['schema'], 'r') as r:
        #    schema_root = etree.fromstring(r.read().encode('utf-8'))

        #schema = etree.XMLSchema(schema_root)

        while self.__run:
            self.logger.debug('SST Client: looking for new tracklets to deliver')

            files = []
            for ext in self.file_ext:
                files += self.inbox.glob(f'**/*.{ext}')

            files = [pathlib.Path(file) for file in files]

            self.logger.info(f'SST Client: {len(files)} files found, delivering')

            rest = http.client.HTTPConnection(
                self.config.get('SST Client', 'Deliver Server'), 
                self.config.getint('SST Client', 'Deliver Port'),
            )

            for file in files:
                with open(file, 'r') as r:
                    tdm_xml = etree.fromstring(r.read())

                #if not schema.validate(tdm_xml):
                #    self.logger.debug(f'SST Client: file "{file}" not valid TDM-XML')
                #    continue

                data = etree.tostring(tdm_xml)
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
                        ret_ = func(xml_request, self.config)
                    else:
                        ret_ = None

                    response = SERVICES[request_tag]['response'].encode('utf-8')
                    if response is None:
                        response = ret_
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
        self.logger.debug(f'SSTServer:__call__:Yielding response')
        yield response
