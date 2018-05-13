from pycrate_asn1dir import RRLP
from pycrate_asn1rt.utils import *

class RrlpCodec:
    def decode_asn1(self, payload):
        rrlp_pdu = RRLP.RRLP_Messages.PDU
        rrlp_pdu.from_uper(payload)
        print(rrlp_pdu.to_asn1())
