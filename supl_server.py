from tls_server import *
from supl_session import *
from supl_logger import logger

class SuplServer(TlsServerCallback):
    def __init__(self):
        self.tls_server = TlsServer(self)
        self.sessions = {}

    def process_client_connected(self, client_fileno):
        if self.sessions.__contains__(client_fileno):
            logger.debug("Error, failed to add session with fileno: %d, session already exists!" % client_fileno)
        else:
            self.sessions[client_fileno] = SuplSession(self, client_fileno)

    def process_client_disconnected(self, client_fileno):
        if self.sessions.__contains__(client_fileno):
            del self.sessions[client_fileno]
        else:
            logger.debug("Error, failed to remove session with fileno: %d, no such session!" % client_fileno)

    def receive(self, client_fileno, rx_data):
        if self.sessions.__contains__(client_fileno):
            self.sessions[client_fileno].receive(rx_data)
        else:
            logger.debug("Error, failed to deliver data to session with fileno: %d, no such session!" % client_fileno)

    def send(self, client_fileno, tx_data):
        if self.sessions.__contains__(client_fileno):
            self.tls_server.send(client_fileno, tx_data)
        else:
            logger.debug("Error, failed to send data to peer with fileno: %d, no such session!" % client_fileno)

    def run(self):
        self.tls_server.run()

    



        
