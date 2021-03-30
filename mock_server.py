import logging

from sst_service import run_server, WsdlService

class ESACore(WsdlService):

    def submitObservationData(self, data, parts):
        ns = '{http://esa.ssa/dpc/2.1/SubmitObservationDataResponseType}'
        return {
            f'{ns}DPCConfirmationCodeType': 'SUCCESSFUL DATA RETRIEVAL',
        }

if __name__ == '__main__':
    host = 'localhost'
    port = 8009
    logging.info('STARTING MOCK SERVER')
    run_server(port, host, Service=ESACore, template_path = 'mock_templates')