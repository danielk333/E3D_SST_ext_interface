import sys
import pathlib
import configparser
import logging

config = configparser.ConfigParser()

CCSDS = './templates/commonSSTDataModel/CCSDS/ndmxml-1.0-master.xsd'

ROOT = pathlib.Path(__file__).resolve().parent
DEBUG = False

if DEBUG:
    level = logging.DEBUG
else:
    level = logging.INFO
logging.basicConfig(
    level=level,
    format='%(asctime)s %(levelname)s %(message)s',
)


path = ROOT/'config.conf'

DEFAULT = {
    'General': {
        'Enable terminal logging': True,
        'Terminal logging level': 'info',
        'Enable file logging': True,
        'File logging level': 'info',
        'Daemon path': '/tmp/daemon-SSTService.pid',
    },
    'SST Server': {
        'host': 'localhost',
        'port': 8000,
        'tdm-output': './data/tracklets',
    },
    'SST Client': {
        'Deliver interval': 60.0,
        'Inbox': './data/tracklets',
        'Archive': './data/archive',
        'File-extensions': 'tdm,odm,xml',
        'Deliver Server': 'localhost',
        'Deliver Port': 32777,
    },
}

config.read_dict(DEFAULT)

if path.exists():
    config.read([path])
else:
    with open(path, 'w') as cfgfile:
        config.write(cfgfile)

HTTP_200 = '200 OK'
HTTP_404 = '404 Not Found'