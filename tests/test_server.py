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
    # 'b': {
    #     'response': SERVICES['b']['response'],
    #     'fail': cfg.HTTP_404,
    # },
}

def test_request_a():

    logger = get_logger(file_level = None, term_level = logging.DEBUG)

    class LoggerWSGIRequestHandler(WSGIRequestHandler):
        def log_message(self, format, *args):
            logger.info("%s - - %s" % (self.address_string(), format%args))

    cfg_dict = {}
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

    for req in test_requests:
        rxml = (pathlib.Path('.')/'tests'/'data'/f'{req}.xml').absolute()
        rxml_err = (pathlib.Path('.')/'tests'/'data'/f'{req}_error.xml').absolute()
        response = send_request(rxml)

        assert response==test_requests[req]['response'], f'{response} =! {test_requests[req]["response"]}'

        response = send_request(rxml_err)

        assert response==test_requests[req]['fail'], f'{response} =! {test_requests[req]["fail"]}'

    server.shutdown()
    server.server_close()
    logger.info('SST Server: STOPPED')
    server_thread.join()
    del server

if __name__=='__main__':
    test_request_a()