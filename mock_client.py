import sys
import pathlib

from lxml import objectify
import lxml.etree

from suds.client import SoapClient, Client
from suds.cache import ObjectCache
from suds.xsd.doctor import Import, ImportDoctor

from config import config, ROOT
from actions import EPOCH

try:
    from astropy.time import TimeDelta
except ImportError:
    TimeDelta = None

def get_client():
    host = config.get('SST Server', 'host')
    port = config.getint('SST Server', 'port')
    return Client(
        f'http://{host}:{port}/SSTService/interface.wsdl',
        location=f'http://{host}:{port}/SSTService/interface',
        cache=None,
    )

def request_tracking(oid):
    client = get_client()
    out = client.service.requestTracking(oid)
    print(out)
    return out

def request_survey(dt):
    client = get_client()
    out = client.service.requestSurvey(EPOCH.iso, (EPOCH + TimeDelta(dt, format='sec')).iso, dt)
    print(out)
    return out




if __name__=='__main__':
    out = request_tracking(0)
    assert out == 'REQUEST APPROVED'

    out = request_tracking(99999)
    assert out == 'REQUEST DENIED'

    out = request_survey(69)
    assert out == 'REQUEST APPROVED'