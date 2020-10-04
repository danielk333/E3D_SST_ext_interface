import http.client
from lxml import etree

import config_mock as cfg

def send_request(file):
    rest = http.client.HTTPConnection(cfg.SST_HOST, cfg.SST_PORT)

    tree = etree.parse(open(file, 'r'))

    data = etree.tostring(tree.getroot())
    header = {
        'Content-Type': 'text/xml',
        'Content-Length': str(len(data)),
    }

    rest.request('POST', '', body=data, headers=header)
    
    response = rest.getresponse()
    raw = response.read().decode("utf-8")
    return raw