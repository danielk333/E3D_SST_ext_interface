import sys
import pathlib
import configparser

config = configparser.ConfigParser()

path = pathlib.Path(__file__).parent / 'config.conf'

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
        'File-extensions': 'tdm,odm',
        'Deliver Server': 'localhost',
        'Deliver Port': 32777,
        'Deliver Path': 'Deliver/Tracklet/Data',
    },
}

config.read_dict(DEFAULT)

if path.exists():
    config.read([path])
else:
    with open(path, 'w') as cfgfile:
        config.write(cfgfile)