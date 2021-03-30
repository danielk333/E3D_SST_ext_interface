import sys
import time
import logging
import threading

from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIRequestHandler

from daemon import Daemon
from log import get_logger
from sst_service import main as service_main


class SSTService(Daemon):

    def __init__(self, config):
        super().__init__(config.get('General', 'Daemon path'))
        self.config = config

        if self.config.getboolean('General', 'Enable terminal logging'):
            tlevel = self.config.get('General', 'Terminal logging level').upper()
            tlevel = getattr(logging, tlevel)
        else:
            tlevel = None

        if self.config.getboolean('General', 'Enable file logging'):
            flevel = self.config.get('General', 'File logging level').upper()
            flevel = getattr(logging, flevel)
        else:
            flevel = None

        self.logger = get_logger(file_level = flevel, term_level = tlevel)


    def abort(self):
        self.__run = False


    def run(self):
        self.__run = True
        
        self.client = SSTClient(self.config, self.logger)

        self.server_thread = threading.Thread(target=service_main)
        self.client_thread = threading.Thread(target=self.client.run)
        
        try:
            self.logger.info('SSTServer: STARTED')
            self.server_thread.start()
            self.client_thread.start()
            while self.__run:
                pass
            self.logger.info('External abort received')
        except KeyboardInterrupt:
            self.logger.info('Service exit received')
        finally:
            self.server.shutdown()
            self.server.server_close()
            self.logger.info('SSTServer: STOPPED')
            self.server_thread.join()
            del self.server
            self.server = None

            self.client.stop()
            self.client_thread.join()
            del self.client
            self.client = None
            


if __name__ == "__main__":
    from config import config

    daemon = SSTService(config)

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
