from binascii import hexlify, unhexlify
from pycrate_asn1dir import ULP
from pycrate_asn1dir import RRLP
from pycrate_asn1rt.utils import *

from supl_logger import logger
from rrlp_session import *

class SuplSession:
    def __init__(self, supl_server, client_fileno):
        self.supl_server = supl_server
        self.client_fileno = client_fileno

        self.rrlp_session = RrlpSession()

    def send(self, supl_message):
        pdu = ULP.ULP.ULP_PDU
        pdu.set_val(supl_message)
        logger.debug(pdu.to_asn1())
        tx_data = pdu.to_uper()

        self.supl_server.send(self.client_fileno, tx_data)

    def receive(self, rx_data):
        string = rx_data.hex()
        logger.debug("[RX][%d]: %s" % (len(string)/2, string))

        pdu = ULP.ULP.ULP_PDU
        pdu.from_uper(rx_data)
        logger.debug(pdu.to_asn1())

        (msgtype, message) = get_val_at(pdu, ["message"])

        if "msSUPLSTART" == msgtype:
            self.send_supl_reponse(message)
        elif "msSUPLPOSINIT" == msgtype:
            self.send_supl_pos(message)
        else:
            logger.debug("Received unexpected message: %s" % msgtype)

    def encode_ulp_pdu_header(self):
        header = {
            "length": 0,
            "version": {"maj": 1, "min": 0, "servind": 0},
            "sessionID": {
                "setSessionID": {
                    "sessionId": 1,
                    "setId": (
                        "imsi", bytes.fromhex('FFFF919448458398')
                    )
                },
                "slpSessionID": {
                    "sessionID": bytes.fromhex("00000001"),
                    "slpId": (
                        "fqdn", "192.168.1.30"
                    )
                }
            },
        }

        return header

    def send_supl_reponse(self, msg_supl_start):
        supl_message = {}

        supl_message.update(self.encode_ulp_pdu_header())
        supl_message["message"] = (
            "msSUPLRESPONSE", {
                "posMethod": "agpsSETbased"
            }
        )

        self.send(supl_message)

    def send_supl_pos(self, msg_supl_pos_init):
        supl_message = {}
        
        supl_message.update(self.encode_ulp_pdu_header())

        rrlp_payload = self.rrlp_session.encode_assit_data()
        supl_message["message"] = (
            "msSUPLPOS", {
                "posPayLoad": (
                    "rrlpPayload", rrlp_payload
                )
            }
        )

        self.send(supl_message)