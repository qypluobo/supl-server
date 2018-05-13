import ssl,socket,time
from common.supl_codec import SuplCodec
from common.parameters import Parameters

class SuplClient:
    def __init__(self):
        self.session_id = 1
        self.slp_session_id = bytes.fromhex("00000001")
        self.codec = SuplCodec()

    def connect(self, fqdn, port):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        #context.load_verify_locations(cafile="security/rootca.pem")
        self.conn = context.wrap_socket(socket.socket(socket.AF_INET))

        print("Connecting to %s:%d..." % (fqdn, port))
        self.conn.connect((fqdn, port))
        print("Connected!")

    def disconnect(self):
        print("Disconnecting...")
        self.conn.close()
        print("Disconnected!")

    def send(self, tx_data):
        string = tx_data.hex()
        print("[TX][%d]: %s" % (len(string)/2, string))

        length = self.conn.send(tx_data)
        print("Sent %d bytes!" % length)

    def recv(self):
        rx_data = self.conn.recv(1024 * 10)
        string = rx_data.hex()
        print("[RX][%d]: %s" % (len(string)/2, string))

        return rx_data

    def run(self):
        self.connect(Parameters.FQDN, Parameters.PORT)

        data = self.codec.encode_supl_start(self)
        self.send(data)

        rx_data = self.recv()
        success = self.codec.decode_asn1(self, rx_data)

        if (success):
            data = self.codec.encode_supl_pos_init(self)
            self.send(data)

            rx_data = self.recv()
            success = self.codec.decode_asn1(self, rx_data)
        
        self.disconnect()

client = SuplClient()
client.run()