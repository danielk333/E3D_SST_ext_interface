from spyne import Application, rpc, ServiceBase, Integer, Unicode

from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


class SSTService(ServiceBase):
    @rpc(Integer, _returns=Unicode)
    def requestTracking(ctx, objectID):
        if ObjectID < 10:
            return 'REQUEST APPROVED'
        else:
            return 'REQUEST DENIED'

    @rpc(Unicode, Unicode, Integer, _returns=Unicode)
    def requestSurvey(ctx, startTime, stopTime, surveySeconds):
        return 'REQUEST APPROVED'

    


application = Application([SSTService], 'http://eiscat3d.com/SSTService',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

wsgi_application = WsgiApplication(application)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()