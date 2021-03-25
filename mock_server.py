import logging
from wsgiref.simple_server import make_server

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

import spyne
import spyne.protocol.soap
import spyne.server.wsgi


class ReciveTDM(spyne.ServiceBase):
    @spyne.rpc(spyne.AnyXml, _returns=spyne.Unicode)
    def get_tdm(ctx, xml_tdm):
        return u'Thanks'


application = spyne.Application(
    [ReciveTDM], 
    'esa.core',              
    in_protocol=spyne.protocol.soap.Soap11(validator='lxml'),
    out_protocol=spyne.protocol.soap.Soap11(),
)
wsgi_application = spyne.server.wsgi.WsgiApplication(application)


if __name__ == '__main__':
    logging.info("Binding to http://localhost:8001")
    server = make_server('localhost', 8001, wsgi_application)
    server.serve_forever()