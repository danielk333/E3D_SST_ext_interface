import sys
import pathlib

from suds.client import Client
from suds.cache import ObjectCache
from suds.xsd.doctor import Import, ImportDoctor

def get_client():
    return Client(
        'http://localhost:8009/ESA_CORE/SSTDataProcessingService/SSTDataProcessingService.wsdl',
        location='http://localhost:8009/ESA_CORE/SSTDataProcessingService/SSTDataProcessingService',
        cache=None,
    )

def test_SSTDataProcessingService():
    client = get_client()

    ns_req = '{http://esa.ssa/dpc/2.1/SubmitObservationDataRequestType}'
    ns_CCSDS = '{urn:ccsds:recommendation:navigation:schema:ndmxml}'
    ns_eCCSDS = '{http://esa.ssa.sst/2.1/CCSDS/}'

    # from lxml import objectify
    # o= objectify.fromstring(xml)

    tdm = client.factory.create(f'{ns_eCCSDS}extendedTdmType')

    tdm._version = '1.0'
    tdm._id = 'CCSDS_TDM_VERS'

    segment = client.factory.create(f'{ns_CCSDS}tdmSegment')

    tdm.body.segment.append(segment)

    inp = client.factory.create(f'{ns_req}SSTTrackingDataObservationType')
    inp.PlanningRequestID = 42
    inp.measures.append(tdm)

    outp = client.service.submitObservationData(inp)

    print(outp)


if __name__=='__main__':
    test_SSTDataProcessingService()
    # client = get_client()
    # print(client)