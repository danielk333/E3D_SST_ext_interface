"""

"""
import sys
import pathlib
import threading
import logging
import shutil
import configparser

sys.path.append(str(pathlib.Path('.').absolute()))

from mock_server import start_mock_server
import config_mock as cfg

from sst import SSTClient
from log import get_logger

def test_send_tdm():

    logger = get_logger(file_level = None, term_level = logging.DEBUG)

    tdm_inbox_path = (pathlib.Path('.')/'tests'/'data'/'tracklets'/'tdm.xml').absolute()
    tdm_archive_path = (pathlib.Path('.')/'tests'/'data'/'archive'/'tdm.xml').absolute()

    cfg_dict = {
        'SST Client': {
            'Archive':  (pathlib.Path('.')/'tests'/'data'/'archive').absolute(),
            'Inbox': (pathlib.Path('.')/'tests'/'data'/'tracklets').absolute(),
            'File-extensions': 'xml',
            'Deliver Port': cfg.MOCK_ESA_PORT,
            'Deliver Server': cfg.MOCK_ESA_HOST,
            'Deliver interval': 1.0,
        },
    }
    config = configparser.ConfigParser()
    config.read_dict(cfg_dict)

    client = SSTClient(config, logger, delivery_log=True)
    thread = threading.Thread(target=client.run)

    server = start_mock_server()

    thread.start()
    while len(client.deliveries) == 0:
        pass

    server.stop()
    client.stop()
    thread.join()

    assert tdm_archive_path.is_file(), 'File was not moved to archive'

    shutil.move(tdm_archive_path, tdm_inbox_path)


if __name__=='__main__':
    test_send_tdm()