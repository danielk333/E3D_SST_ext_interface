import sys
import pathlib

from lxml import objectify
import lxml.etree

from suds.client import SoapClient, Client
from suds.cache import ObjectCache
from suds.xsd.doctor import Import, ImportDoctor

from actions import simulate_measurements

def get_client():
    return Client(
        'http://localhost:8009/ESA_CORE/SSTDataProcessingService/SSTDataProcessingService.wsdl',
        location='http://localhost:8009/ESA_CORE/SSTDataProcessingService/SSTDataProcessingService',
        cache=None,
    )

def test_SSTDataProcessingService():
    client = get_client()

    method = client.wsdl.services[0].ports[0].methods['submitObservationData']
    message = method.binding.input.get_message(method, [], {})

    ns_req = '{http://esa.ssa/dpc/2.1/SubmitObservationDataRequestType}'
    ns_CCSDS = '{urn:ccsds:recommendation:navigation:schema:ndmxml}'
    ns_eCCSDS = '{http://esa.ssa.sst/2.1/CCSDS/}'

    NSMAP = {
        'tns': ns_req[1:-1],
        'CCSDS': ns_CCSDS[1:-1],
        'eCCSDS': ns_eCCSDS[1:-1],
    }

    message = lxml.etree.XML(str(message).encode())

    measure = message.findall(f'.//{ns_req}measure')[0]

    measures = lxml.etree.Element(f'{ns_req}measures', nsmap = NSMAP)
    measures.attrib[f'{ns_eCCSDS}id'] = 'CCSDS_TDM_VERS'
    measures.attrib[f'{ns_eCCSDS}version'] = '2.0'
    measure.append(measures)
    
    dont_ns = [
        'CREATION_DATE',
        'ORIGINATOR',
        'TIME_SYSTEM',
        'PARTICIPANT_1',
        'PARTICIPANT_2',
        'PARTICIPANT_3',
    ]
    delte_tags = [
        'MESSAGE_ID',
        'COMMENT',
    ]

    tdms = simulate_measurements(0)

    tdm = lxml.etree.XML(tdms[0])
    for tag in tdm.iter():
        if tag.tag in delte_tags:
            tag.getparent().remove(tag)
            continue
        if tag.tag not in dont_ns:
            tag.tag = f'{ns_eCCSDS}{tag.tag}'

    for el in tdm:
        measures.append(el)

    outp = client.service.submitObservationData(__inject={'msg': lxml.etree.tostring(message, pretty_print=True)})

    print(outp)


if __name__=='__main__':
    test_SSTDataProcessingService()
    # client = get_client()
    # print(client)