"""

"""
import sys
import pathlib
import threading
import logging
import shutil
import configparser

from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIRequestHandler

sys.path.append(str(pathlib.Path('.').absolute()))

from mock_client import send_request
import config_mock as cfg

from sst import SSTServer
from log import get_logger
from config import SERVICES

test_requests = {
    'a': {
        'response': cfg.HTTP_200,
        'fail': cfg.HTTP_404,
    },
    'b': {
        'response': '<status>OK</status>',
        'fail': cfg.HTTP_404,
    },
    'd': {
        'response': open(pathlib.Path('.')/'templates'/'responses'/'d.xml', 'r').read(),
        'fail': cfg.HTTP_404,
    },
}

logger = get_logger(file_level = None, term_level = logging.DEBUG)

def template_test_request(name):

    class LoggerWSGIRequestHandler(WSGIRequestHandler):
        def log_message(self, format, *args):
            logger.info("%s - - %s" % (self.address_string(), format%args))

    cfg_dict = {
        'SST Server': {
                'tdm-output': (pathlib.Path('.')/'tests'/'data'/'tracklets').absolute(),
            }
    }
    config = configparser.ConfigParser()
    config.read_dict(cfg_dict)

    app = SSTServer(config, logger)
    
    server = make_server(
        cfg.SST_HOST, 
        cfg.SST_PORT, 
        app,
        handler_class=LoggerWSGIRequestHandler,
    )

    server_thread = threading.Thread(target=server.serve_forever)

    server_thread.start()

    rxml = (pathlib.Path('.')/'tests'/'data'/f'{name}.xml').absolute()
    rxml_err = (pathlib.Path('.')/'tests'/'data'/f'{name}_error.xml').absolute()
    response = send_request(rxml)

    response_err = send_request(rxml_err)

    server.shutdown()
    server.server_close()
    logger.info('SST Server: STOPPED')
    server_thread.join()

    assert response==test_requests[name]['response'], f'{response} =! {test_requests[name]["response"]}'
    assert response_err==test_requests[name]['fail'], f'{response_err} =! {test_requests[name]["fail"]}'

    del server


def test_request_a():
    template_test_request('a')

def test_request_b():
    template_test_request('b')

def test_request_d():
    template_test_request('d')


if __name__=='__main__':
    for key in test_requests:
        template_test_request(key)