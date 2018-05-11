import ssl,socket,time
from pycrate_asn1dir import ULP
from pycrate_asn1dir import RRLP
from pycrate_asn1rt.utils import *

class SuplClient:
    def __init__(self):
        self.supl_ver_maj = 2
        self.supl_ver_min = 0
        self.supl_ver_servid = 0

        self.lpp_ver_maj = 14
        self.lpp_ver_tech = 4
        self.lpp_ver_editor = 0

        self.gsm_refMCC = 244
        self.gsm_refMNC = 5
        self.gsm_refLAC = 23010
        self.gsm_refCI = 12720

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

    def send(self, tx_data):
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
        self.send_supl_start_lpp()
        rx_data = self.recv()
        success = self.process_supl_response(rx_data)
        if (success):
            self.send_supl_pos_init_lpp()
            self.recv()
        
        self.disconnect()

    def process_supl_response(self, rx_data):
        pdu = ULP.ULP.ULP_PDU
        pdu.from_uper(rx_data)

        (msgtype, message) = get_val_at(pdu, ["message"])
        if msgtype == "msSUPLPOS":
            self.slpSessionID = get_val_at(pdu, ["sessionID", "slpSessionID", "sessionID"])
            return True

        print("Error, expected msSUPLPOS but received %s" % msgtype)
        return False

    def send_supl_start_rrlp(self):
        message = {
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

        tx_data = self.encode_supl_message(message)
        self.send(tx_data)

    def send_supl_pos_init_rrlp(self):
        message = {
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

        tx_data = self.encode_supl_message(message)
        self.send(tx_data)

    def encode_supl_message(self, supl_message):
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

        return tx_data

    def send_supl_start_lpp(self):
        message = {
            "length": 0,
            "version": {
                "maj": self.supl_ver_maj,
                "min": self.supl_ver_min,
                "servind": self.supl_ver_servid
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
                            "rrlp": False,
                            "rrc": False,
                            "ver2-PosProtocol-extension": {
                                "lpp": True,
                                "posProtocolVersionLPP": {
                                    "majorVersionField": self.lpp_ver_maj,
                                    "technicalVersionField": self.lpp_ver_tech,
                                    "editorialVersionField": self.lpp_ver_editor
                                }
                            }
                        },
                    },
                    "locationId": {
                        "cellInfo": (
                            "gsmCell", {
                                "refMCC": self.gsm_refMCC,
                                "refMNC": self.gsm_refMNC,
                                "refLAC": self.gsm_refLAC,
                                "refCI": self.gsm_refCI,
                            }
                        ),
                        "status": 'current'
                    },
                }
            )
        }

        tx_data = self.encode_supl_message(message)
        self.send(tx_data)

    def send_supl_pos_init_lpp(self):
        message = {
            "length": 0,
            "version": {
                "maj": self.supl_ver_maj,
                "min": self.supl_ver_min,
                "servind": self.supl_ver_servid
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
                            "rrlp": False,
                            "rrc": False,
                            "ver2-PosProtocol-extension": {
                                "lpp": True,
                                "posProtocolVersionLPP": {
                                    "majorVersionField": self.lpp_ver_maj,
                                    "technicalVersionField": self.lpp_ver_tech,
                                    "editorialVersionField": self.lpp_ver_editor
                                }
                            }
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
                                "refMCC": self.gsm_refMCC,
                                "refMNC": self.gsm_refMNC,
                                "refLAC": self.gsm_refLAC,
                                "refCI": self.gsm_refCI,
                            }
                        ),
                        "status": 'current'
                    },
                }
            )
        }

        tx_data = self.encode_supl_message(message)
        self.send(tx_data)

client = SuplClient()
client.run()