import socket
import ssl
import select
import os
from supl_logger import logger

class TlsServerCallback:
    def process_client_connected(self, client_sock):
        pass
    
    def process_client_disconnected(self, client_sock):
        pass

    def receive(self, fileno, data):
        pass

class TlsServer:
    def __init__(self, callback):
        self.callback = callback

        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        self.epoll = select.epoll()

        self.is_running = True
        self.clients = {}
    
    def add_client(self, client, address):
        self.clients[client.fileno()] = (client, address)
        self.epoll.register(client.fileno(), select.EPOLLIN)

        self.callback.process_client_connected(client.fileno())

        logger.debug("Client is connected, address: %s:%d" % address)   # address format is ('192.168.1.30', 55908)

    def del_client(self, fileno):
        if self.clients.__contains__(fileno):
            (client, address) = self.clients[fileno]
            self.epoll.unregister(fileno)
            client.close()
            del self.clients[fileno]

            self.callback.process_client_disconnected(fileno)

            logger.debug("Client is disconnected, address: %s:%d" % (address[0], address[1]))

    def receive(self, fileno):
        if self.clients.__contains__(fileno):
            data = self.clients[fileno][0].recv(1024)
            if data == b"":
                self.del_client(fileno)
                return

            self.callback.receive(fileno, data)

            #string = data.hex()
            #logger.debug("[RX][%d]: %s" % (len(string)/2, string))

    def send(self, fileno, data):
        if (data != None and self.clients.__contains__(fileno)):
            (client, address) = self.clients[fileno]

            logger.debug("Sending %d bytes data to client: %s:%d" % (len(data), address[0], address[1]))
            length = client.send(data)
            logger.debug("Sent %d bytes data to client: %s:%d" % (length, address[0], address[1]))
        else:
            logger.debug("Failed to send data to: %s:%d, no such client!" % (address[0], address[1]))

    def run(self):
        self.ssl_context.load_cert_chain(certfile="security/server.pem", keyfile="security/server.key") # need key without password

        logger.debug('Create socket')
        serversocket = socket.socket()
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(('192.168.1.30', 7275))

        logger.debug('Listenning...')
        serversocket.listen()

        with self.ssl_context.wrap_socket(serversocket, server_side=True) as ssock:
            self.epoll.register(ssock.fileno(), select.EPOLLIN)
            try:
                while self.is_running:
                    events = self.epoll.poll(1)
                    for fileno, event in events:
                        if fileno == ssock.fileno():
                            client, address = ssock.accept()
                            self.add_client(client, address)
                        elif event & select.EPOLLIN:
                            self.receive(fileno)
                        #elif event & select.EPOLLOUT:
                        #    self.send(fileno)
                        elif event & select.EPOLLHUP:
                            self.del_client(fileno)
            finally:
                self.epoll.unregister(ssock.fileno())
                self.epoll.close()
                ssock.close()