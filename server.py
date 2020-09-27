import sys
import time
import logging
import threading

from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIRequestHandler

from daemon import Daemon
from log import get_logger
from sst import SSTApplication, TrackletSender

SST_HOST = 'localhost'
SST_PORT = 32769


class SSTService(Daemon):
    def run(self):
        logger = get_logger(file_level = logging.INFO, term_level = logging.INFO)

        class LoggerWSGIRequestHandler(WSGIRequestHandler):
            def log_message(self, format, *args):
                logger.info("%s - - %s" % (self.address_string(), format%args))

        self.server = make_server(
            SST_HOST, 
            SST_PORT, 
            SSTApplication(logger),
            handler_class=LoggerWSGIRequestHandler,
        )

        self.client = TrackletSender(logger)

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.client_thread = threading.Thread(target=self.client.run)
        
        try:
            logger.info('SST Server: STARTED')
            self.server_thread.start()
            self.client_thread.start()
            while True:
                pass
        except KeyboardInterrupt:
            logger.info('Service exit received\n')
        finally:
            self.server.shutdown()
            self.server.server_close()
            logger.info('SST Server: STOPPED')
            self.server_thread.join()
            del self.server
            self.server = None

            self.client.stop()
            self.client_thread.join()
            del self.client
            self.client = None
            


if __name__ == "__main__":

    daemon = SSTService('/tmp/daemon-SSTService.pid')

    if len(sys.argv) == 2:
        if 'run' == sys.argv[1]:
            daemon.run()
        elif 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s run|start|stop|restart" % sys.argv[0])
        sys.exit(2)
