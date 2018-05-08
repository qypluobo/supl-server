import ssl,socket,time
from pycrate_asn1dir import ULP
from pycrate_asn1dir import RRLP
from pycrate_asn1rt.utils import *

class SuplClient:
    def __init__(self):
        self.fqdn = 'supl.vodafone.com'
        #self.fqdn = '192.168.1.30'

        self.imsi = bytes.fromhex('FFFF919448458398')
        self.sessionId = 1
        self.slpSessionID = bytes.fromhex("00000001")

    def connect(self, fqdn, port):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_verify_locations(cafile="security/rootca.pem")
        self.conn = context.wrap_socket(socket.socket(socket.AF_INET))

        print("Connecting to %s:%d..." % (fqdn, port))
        self.conn.connect((fqdn, port))
        print("Connected!")

    def disconnect(self):
        self.conn.close()

    def send(self, supl_message):
        pdu = ULP.ULP.ULP_PDU

        # 1. Encode data to get the length in SUPL header
        pdu.set_val(supl_message)
        tx_data = pdu.to_uper()
        length = len(tx_data)

        # 2. Correct the length in SUPL header
        supl_message["length"] = length
        pdu.set_val(supl_message)
        tx_data = pdu.to_uper()

        print(pdu.to_asn1())

        string = tx_data.hex()
        print("[TX][%d]: %s" % (len(string)/2, string))

        length = self.conn.send(tx_data)
        print("Sent %d bytes!" % length)

    def recv(self):
        rx_data = self.conn.recv(1024 * 10)
        string = rx_data.hex()
        print("[RX][%d]: %s" % (len(string)/2, string))

        pdu = ULP.ULP.ULP_PDU
        pdu.from_uper(rx_data)
        print(pdu.to_asn1())

        (msgtype, message) = get_val_at(pdu, ["message"])
        if msgtype == "msSUPLPOS":
            (payload_type, payload) = message["posPayLoad"]
            if payload_type == "rrlpPayload":
                rrlp_pdu = RRLP.RRLP_Messages.PDU
                rrlp_pdu.from_uper(payload)
                print(rrlp_pdu.to_asn1())

        return rx_data

    def run(self):
        self.connect(self.fqdn, 7275)
        self.send_supl_start()
        rx_data = self.recv()
        self.process_supl_response(rx_data)

        self.send_supl_pos_init()
        self.recv()
        self.disconnect()

    def process_supl_response(self, rx_data):
        pdu = ULP.ULP.ULP_PDU
        pdu.from_uper(rx_data)

        self.slpSessionID = get_val_at(pdu, ["sessionID", "slpSessionID", "sessionID"])

    def send_supl_start(self):
        supl_start = {
            "length": 0,
            "version": {
                "maj": 1,
                "min": 0,
                "servind": 0
            },
            "sessionID": {
                "setSessionID": {
                    "sessionId": self.sessionId,
                    "setId": (
                        "imsi", self.imsi
                    )
                }
            },
            "message": (
                "msSUPLSTART", {
                    "sETCapabilities": {
                        "posTechnology": {
                            "agpsSETassisted": False,
                            "agpsSETBased": True,
                            "autonomousGPS": False,
                            "aflt": False,
                            "ecid": False,
                            "eotd": False,
                            "otdoa": False,
                        },
                        "prefMethod": "agpsSETBasedPreferred",
                        "posProtocol": {
                            "tia801": False,
                            "rrlp": True,
                            "rrc": False,
                        },
                    },
                    "locationId": {
                        "cellInfo": (
                            "gsmCell", {
                                "refMCC": 244,
                                "refMNC": 5,
                                "refLAC": 23010,
                                "refCI": 12720,
                            }
                        ),
                        "status": 'current'
                    },
                }
            )
        }

        self.send(supl_start)

    def send_supl_pos_init(self):
        supl_pos_init = {
            "length": 0,
            "version": {
                "maj": 1,
                "min": 0,
                "servind": 0
            },
            "sessionID": {
                "setSessionID": {
                    "sessionId": self.sessionId,
                    "setId": (
                        "imsi", self.imsi
                    )
                },
                "slpSessionID": {
                    "sessionID": self.slpSessionID,
                    "slpId": (
                        "fqdn", self.fqdn
                    )
                }
            },
            "message": (
                "msSUPLPOSINIT", {
                    "sETCapabilities": {
                        "posTechnology": {
                            "agpsSETassisted": False,
                            "agpsSETBased": True,
                            "autonomousGPS": False,
                            "aflt": False,
                            "ecid": False,
                            "eotd": False,
                            "otdoa": False,
                        },
                        "prefMethod": "agpsSETBasedPreferred",
                        "posProtocol": {
                            "tia801": False,
                            "rrlp": True,
                            "rrc": False,
                        },
                    },
                    "requestedAssistData": {
                        "almanacRequested": True,
                        "utcModelRequested": False,
                        "ionosphericModelRequested": False,
                        "dgpsCorrectionsRequested": False,
                        "referenceLocationRequested": False,
                        "referenceTimeRequested": False,
                        "acquisitionAssistanceRequested": False,
                        "realTimeIntegrityRequested": False,
                        "navigationModelRequested": False,
                    },
                    "locationId": {
                        "cellInfo": (
                            "gsmCell", {
                                "refMCC": 244,
                                "refMNC": 5,
                                "refLAC": 23010,
                                "refCI": 12720,
                            }
                        ),
                        "status": 'current'
                    },
                }
            )
        }

        self.send(supl_pos_init)

client = SuplClient()
client.run()