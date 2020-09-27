import http.client
from lxml import etree

SST_HOST = 'localhost'
SST_PORT = 32769


def send_request():
    rest = http.client.HTTPConnection(SST_HOST, SST_PORT)

    data = open('./templates/SubmitObservationDataRequestType.xml', 'r').read().encode("UTF-8")
    header = {
    'Content-Type': 'text/xml',
    'Content-Length': str(len(data)),
    }

    rest.request('POST', '', body=data, headers=header)
    
    response = rest.getresponse()
    raw = response.read().decode("utf-8")
    print(raw)


send_request()