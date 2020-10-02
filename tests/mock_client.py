import http.client
from lxml import etree

import test_configuration as cfg

def send_request(request_tag):
    rest = http.client.HTTPConnection(cfg.SST_HOST, cfg.SST_PORT)

    tree = etree.parse(cfg.ROOT + / 'requests' / f'{cfg.HANDLE_REQUESTS[request_tag]}.xml')

    data = etree.tostring(tree.getroot())
    header = {
        'Content-Type': 'text/xml',
        'Content-Length': str(len(data)),
    }

    rest.request('POST', '', body=data, headers=header)
    
    response = rest.getresponse()
    raw = response.read().decode("utf-8")
    return raw