from pycrate_asn1dir import ULP
from pycrate_asn1rt.utils import get_val_at
from .parameters import Parameters
from .rrlp_codec import RrlpCodec

class SuplCodec:
    def __init__(self):
        self.rrlp_codec = RrlpCodec()

    #
    # Public methods
    #
    def encode_supl_start(self, session_ctx):
        message = self.encode_ulp_header(session_ctx.session_id, None)
        set_capa = self.encode_set_capabilities()
        location_id = self.encode_location_id()

        message["message"] = (
            "msSUPLSTART", {
                "sETCapabilities": set_capa,
                "locationId": location_id
            }
        )
        data = self.encode_asn1(message)
        return data
    
    def encode_supl_pos_init(self, session_ctx):
        message = self.encode_ulp_header(session_ctx.session_id, session_ctx.slp_session_id)
        set_capa = self.encode_set_capabilities()
        location_id = self.encode_location_id()

        message["message"] = (
            "msSUPLPOSINIT", {
                "sETCapabilities": set_capa,
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
                "locationId": location_id,
            }
        )
        data = self.encode_asn1(message)
        return data

    def decode_asn1(self, session_ctx, rx_data):
        if 0 == len(rx_data):
            print("Error, received 0 bytes!")
            return

        pdu = ULP.ULP.ULP_PDU
        pdu.from_uper(rx_data)
        print(pdu.to_asn1())

        # print payload
        (msgtype, message) = get_val_at(pdu, ["message"])
        if message.__contains__("posPayLoad"):
            (payload_type, payload) = message["posPayLoad"]
            if payload_type == "rrlpPayload":
                self.rrlp_codec.decode_asn1(payload)

        (msgtype, message) = get_val_at(pdu, ["message"])
        if msgtype == "msSUPLRESPONSE":
            return self.decode_supl_response(session_ctx, pdu)
        elif msgtype == "msSUPLPOS":
            # TBD
            return True

        print("Error, unexpected message type: %s" % msgtype)
        return False

    def decode_supl_response(self, session_ctx, pdu):
        session_ctx.slp_session_id = get_val_at(pdu, ["sessionID", "slpSessionID", "sessionID"])
        return True


    #
    # Private methods
    #
    def encode_asn1(self, message):
        pdu = ULP.ULP.ULP_PDU

        # 1. Encode data to get the length in SUPL header
        pdu.set_val(message)
        tx_data = pdu.to_uper()
        length = len(tx_data)

        # 2. Correct the length in SUPL header
        message["length"] = length
        pdu.set_val(message)
        tx_data = pdu.to_uper()

        print(pdu.to_asn1())

        return tx_data

    def encode_ulp_header(self, session_id, slp_session_id):
        message = {
            "length": 0,
            "version": {
                "maj": Parameters.SUPL_VER_MAJ,
                "min": Parameters.SUPL_VER_MIN,
                "servind": Parameters.SUPL_VER_SERVID
            },
            "sessionID": {
                "setSessionID": {
                    "sessionId": session_id,
                    "setId": (
                        "imsi", Parameters.IMSI
                    )
                }
            },
        }

        if None != slp_session_id:
            message["sessionID"]["slpSessionID"] = {
                "sessionID": slp_session_id,
                "slpId": (
                    "fqdn", Parameters.FQDN
                )
            }
        return message
        
    def encode_set_capabilities(self):
        set_capabbilities = {
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
                "rrlp": Parameters.RRLP_ENABLED,
                "rrc": False,
            },
        }

        if Parameters.LPP_ENABLED:
            set_capabbilities["posProtocol"]["ver2-PosProtocol-extension"] = {
                "lpp": Parameters.LPP_ENABLED,
                "posProtocolVersionLPP": {
                    "majorVersionField": Parameters.LPP_VER_MAJ,
                    "technicalVersionField": Parameters.LPP_VER_TECH,
                    "editorialVersionField": Parameters.LPP_VER_EDITOR
                }
            }

        return set_capabbilities

    def encode_location_id(self):
        location_id = {
            "cellInfo": (
                "gsmCell", {
                    "refMCC": Parameters.GSM_REF_MCC,
                    "refMNC": Parameters.GSM_REF_MNC,
                    "refLAC": Parameters.GSM_REF_LAC,
                    "refCI": Parameters.GSM_REF_CI,
                }
            ),
            "status": 'current'
        }
        return location_id