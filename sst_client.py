#!/usr/bin/env python3


"""
"""
import time
import glob
import pathlib
import shutil
import os

from suds.client import Client
from suds.cache import ObjectCache

import xmlschema


class SSTClient:
    '''Main automatic client for delivering data generated by the EISCAT 3D SST Services.

    :param logger logger: A logger instance, all calls to the application from the simple_server will be logged to this instance.
    :param configparser.ConfigParser config: The server configuration.
    :param bool delivery_log: If :code:`True` a internal list is kept of all files/data that has been delivered, can be considered a intentional memory leak and should only be used for testing.
    '''
    def __init__(self, config, logger, schema_path, delivery_log=False):
        self.logger = logger
        self.config = config
        self.delivery_log = delivery_log
        self.deliveries = []

        self._dry_run = False

        inbox = config.get('SST Client', 'Inbox')
        inbox = pathlib.Path(inbox).absolute()

        self.inbox = inbox
        self.logger.debug(f'SSTClient: inbox={self.inbox}')

        archive = self.config.get('SST Client', 'Archive')
        archive = pathlib.Path(archive).absolute()

        self.archive = archive
        self.logger.debug(f'SSTClient: archive={self.archive}')

        self.file_ext = self.config.get('SST Client', 'File-extensions').split(',')
        self.file_ext = [x.strip() for x in self.file_ext]
        self.logger.debug(f'SSTClient: file extensions={self.file_ext}')

        self.schema = xmlschema.XMLSchema(schema_path)



    def run(self):
        self.logger.info('SSTClient: STARTED')
        self.__run = True

        while self.__run:
            self.logger.debug('SSTClient: looking for new tracklets to deliver')

            files = []
            for ext in self.file_ext:
                files += self.inbox.glob(f'**/*.{ext}')

            files = [pathlib.Path(file) for file in files]

            self.logger.info(f'SSTClient: {len(files)} files found, delivering')

            for file in files:
                with open(file, 'r') as r:
                    xml_data = r.read()

                try:
                    self.schema.decode(xml_data)
                except Exception as e:
                    self.logger.debug(f'SST Client: file "{file}" not valid TDM-XML:')
                    self.logger.exception(e)

                client = Client('http://localhost:8001/?wsdl', cache=None)
                out = client.service.get_tdm(xml_data)
                
                if out:
                    if not self._dry_run:
                        shutil.move(file, self.archive / file.name)
                    self.logger.info(f'SSTClient: Delivery completed "{out}"')
                    if self.delivery_log:
                        self.deliveries += [file]
                else:
                    self.logger.info(f'SSTClient: Delivery failed "{out}"')

            time.sleep(self.config.getfloat('SST Client', 'Deliver interval'))


    def stop(self):
        self.__run = False
        self.logger.info('SST Client: STOPPED')


if __name__ == '__main__':
    from config import CCSDS
    from config import config as cfg
    import logging

    client = SSTClient(cfg, logging, CCSDS)
    client._dry_run = True

    client.run()