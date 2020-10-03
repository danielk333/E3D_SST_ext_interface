import sys
import pathlib
import configparser
import lxml

import services 

config = configparser.ConfigParser()

ROOT = pathlib.Path(__file__).parent

path = ROOT / 'config.conf'

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
        'port': 32769,
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

SERVICES = {
    'a': {
        'action': services.simulate_measurements,
        'response': HTTP_200,
        'schema': ROOT / 'templates' /' services' / 'a.xsd',
    },
    'b': {
        'action': services.check_status,
        'response': open(ROOT / 'templates' /' responses' / 'b.xml', 'r').read(),
        'schema': ROOT / 'templates' /' services' / 'b.xsd',
    },
}

REQUESTS = {
    'TDM': {
        'path': '/',
        'response': HTTP_200,
        'schema': ROOT / 'templates' /' CCSDS' / 'ndmxml-1.0-tdm-2.0.xsd',
    },
}