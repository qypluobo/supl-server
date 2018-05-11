from binascii import hexlify, unhexlify
from pycrate_asn1dir import ULP
from pycrate_asn1dir import RRLP
from pycrate_asn1dir import LPP
from pycrate_asn1dir import LPPe
from pycrate_asn1rt.utils import *

class Playground:
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

        self.imsi = bytes.fromhex('FFFF919448458398')
        self.sessionId = 1
        self.slpSessionID = bytes.fromhex("00000001")
        self.fqdn = 'supl.vodafone.com'

    #################### SUPL test code ##################################
    def test_supl(self):
        raw_data = "001b01000080004ffffe465121160e604102400f40156788c6c080"
        pdu = ULP.ULP.ULP_PDU
        pdu.from_uper(unhexlify(raw_data))
        asn1 = pdu.to_asn1()
        print(asn1)

        length = get_val_at(pdu, ["length"])
        print("length: %d" % length)

        version = get_val_at(pdu, ["version"])
        print("version: %d.%d.%d" %
            (version["maj"], version["min"], version["servind"]))

        set_session_id = get_val_at(pdu, ["sessionID", "setSessionID"])
        imsi = set_session_id["setId"][1]
        print("sessionId: %d, imsi: %s" % (set_session_id["sessionId"], imsi.hex()))

        (msgtype, message) = get_val_at(pdu, ["message"])
        print(msgtype)
        print(message)

        setCaps = message["sETCapabilities"]
        if setCaps["prefMethod"] == "agpsSETassistedPreferred":
            print("agpsSETassistedPreferred:")
        elif setCaps["prefMethod"] == "agpsSETBasedPreferred":
            print("agpsSETBasedPreferred:")
        else:
            print("noPreference:")

        # prefMethod = ULP.SUPL_START.PrefMethod
        # print(prefMethod._cont)


        v = {
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
            "message": (
                "msSUPLRESPONSE", {
                    "posMethod": "agpsSETbased"
                }
            )
        }

        pdu = ULP.ULP.ULP_PDU
        pdu.set_val(v)
        print(pdu.to_asn1())
        print(pdu.to_uper())

    #################### RRLP test code ##################################
    def test_rrlp(self):
        raw_data = "251B7AAA9B2DF36D80F360B0F36010F361E0F36050F361C0F360D0F361F0F36120F36020F36030F36170F361B20B8C0F82513DE00C8EEEE00C2BF6C0400154D134228DC0ED924087FBCA34D9FA01FF2CD49C977EBB3199D1CC5F7793603D13E0984E8A10D3D6C367E7DFF37650CABDE00DE9ECD9BCAAA66896062F1FE89D5B1C2C200024689A1146E076C92043FDE4CA6CFB00FFD958E1D3B1D5783D7E7B073BBB201D6A39E439BD0866CD89B3E98FF61B75B007100515068D66752374E178470FF49FAD478210003A344D08A3703B649021FEF254367E807F9D929ABA1E0AC9D3CA502192196C2495778A479A8436F2ACD9F9F80472C2EE5F57FD1A6B12545998533F4A4BB7FAA6B9DC1E08000C1A268451B81DB24810FF79319B3F403FF4C861271F65664380A6FF731C8008F626211A6F421A5BD26CFCFC01ED7D6DFAE401053A106C64FF83D44547FBFD259C5A228400058D134228DC0ED924087FBCA28D9F601FFC2D61DF86EFAF76EB67D2758635009ED4669131A10CD53E367D25FF60B9339866002E9E217E1A715949AABEB1FEA4BA712702000A6689A1146E076C92043FDE4D46CFD00FF9579D76BAB9D3F936A6D31CBB65802CEB724DE05086DC759B3F3F002E0C76E9CD001F5030779F21CD4D9CD824FF59E2FB99A100038344D08A3703B649021FEF26B367E807FFD7363220D12BA34B96C5DCA0B8C13B4BC266EFE84385C68D9F9F804486E9B4017FFAA72E67918F2430312C627FAC0E7795F08000E9A268451B81DB24810FF79409B3F4040109DF077034961D8B763D4B10300020631B33797421A95146CFCFC002C1BB5EEAC0055382B0F7C7990AB03C08BFD4C9B89090400050D134228DC0ED924087FBC97CD9FA02006117BB17833A89AB27CF4FD78FF0506BF469BF9A10DB81A367E7DFEF81EE0CEEDFF2E9FC3404E4692BC3C03D9FEAFF5EA60820003A689A1146E076C92043FDE50A6CFD01008B0DC24BDBD5B4E606D7FEC3DD7005437D3C4D8D08715B01B3F3B0020B24B22F5004D4E47EF4F47BB23EE32C8FF4810EC90610FC10344D08A3703B649021FEF256367E80801B870541DF330031BA17EB35E39C141EEF66136E8435F95CD9F9F7FECDA4568A58055A7E5D489AAA7A53F43857FA23F6E0570800039A268451B81DB24810FF79431B3F403FFE3CCFC922456F05DC6224611D3C070F3A1519C7421A7E8C6CFCCBFF5566268523FE7D330B6854FAD4B1BCB1F3FD21048E31704FEFF5704FAFAFFFFFAFFFFFFFCC79B25130F259AF007CFEC724B6FABE01421A005D29BB3203683FC6BEF51FF8324C0C70974FAA401421ABA583F0667F5825BD8F524DFE841544C717B0FA8601421B6EB22BBB23B757F89B7B0E601085704C7069AFA6C014219E4B06F47319B5D339612FDA000A13D6C7245EFAC2014219025C7BE6A52B0E4D8A1F6B1FF8CBB14C7156EFA9A01421A0D5E3B42310B340752AD35DFF0E3948C72302FA960142181E0670C8D935BB0916C8E66001010DCC70E06FA9E01421969066B7B9609BEFDFCC3866001238B2C717D4FA88014219A8B1E32C1F7971934E732F600951258C6CF18FA54014219163A940B8ECCAA05DFC83EE001675A4C739BAFA84014218F9B73BA34E49E7D67D2D58DFF98394EC7229CFABC014219C711197982957E7D9256E72001A9DF6C718E4FAB201421B430DB552606AA8D35E86E6E001CA748C6EE20FA6801421A9700BC73370038AA0C82A2E001EA47CC73A50FA8401421923B8C5EB28EF1B3C30730760020C902C7348CFAB401421C0E0B7D5E6EE34AE43F3EE4600A2EBD0C70886FA9A014219DA5963B969D07028782AFFE00A4A0F0C73146FAB801421AB80F529F5E41BDDB92328C200A645BAC6ED02FA4C01422C34A9594F9CBB2E694AC984E002990C0C70104FA9401421AC458D3FE8056C7AD233A95E00AA7A3EC6E8CAFA4201421778AD6E647FF4D6BCEE74A0DFE2CC992C70210FA90014218130650E43EA67285C534C72002E7114C6FF68FA84014219A3596A212C7B045328ACF3600307A28C7299EFA6E014219BDB2666B44D691B0E4126A1FF322DA4C7118EFA4E0142196DB0AA6708B9B1855EA8D1A02345FE6C72DB2FAA401421A3A071ACB1FF8ECF3409D61200374008C738D4FA8001421A15B91F1683EA9338962FB9A00B80B52C73630FAB801421AB00C593F4E31E950C295799FF3A35A0C702A6FA7E01421B3761036C01C88812F45F15DFFBC8F66C71B7EFAA4014219995F3CC0F52969F76239219FFBE209CC713C0FAAA014219A906CF202B4A612DAB7A78200886880A0800000000"
        pdu = RRLP.RRLP_Messages.PDU
        pdu.from_uper(unhexlify(raw_data))

        v = {
            "referenceNumber": 1,
            "component": (
                "assistanceData", {
                    "gps-AssistData": {
                        "controlHeader": {
                            "referenceTime": {
                                "gpsTime": {
                                    "gpsTOW23b": 2792237,
                                    "gpsWeek": 973
                                },
                                "gpsTowAssist": []
                            },
                            "refLocation": {
                                "threeDLocation": bytes.fromhex('905C607C1289EF0064777700615F')
                            },
                            "navigationModel": {
                                "navModelList": []
                            },
                            "ionosphericModel": {
                                "alfa0": 11,
                                "alfa1": 2,
                                "alfa2": -1,
                                "alfa3": -1,
                                "beta0": 43,
                                "beta1": 2,
                                "beta2": -3,
                                "beta3": -3
                            },
                            "utcModel": {
                                "utcA1": -3,
                                "utcA0": -2,
                                "utcTot": 99,
                                "utcWNt": 205,
                                "utcDeltaTls": 18,
                                "utcWNlsf": 137,
                                "utcDN": 7,
                                "utcDeltaTlsf": 18
                            },
                            "almanac": {
                                "alamanacWNa": 205,
                                "almanacList": []
                            },
                            "realTimeIntegrity": [3, 17]
                        }
                    }
                }
            )
        }

        gpsTowAssit1 = {"satelliteID": 24, "tlmWord": 973, "antiSpoof": 1, "alert": 0, "tlmRsvdBits": 0}
        gpsTowAssit2 = {"satelliteID": 11, "tlmWord": 973, "antiSpoof": 1, "alert": 0, "tlmRsvdBits": 0}
        gpsTowAssit3 = {"satelliteID": 1, "tlmWord": 973, "antiSpoof": 1, "alert": 0, "tlmRsvdBits": 0}

        v["component"][1]["gps-AssistData"]["controlHeader"]["referenceTime"]["gpsTowAssist"].append(gpsTowAssit1)

        navModelList1 = {
            "satelliteID": 24,
            "satStatus": (
                "newSatelliteAndModelUC", {
                    "ephemCodeOnL2": 1,
                    "ephemURA": 0,
                    "ephemSVhealth": 0,
                    "ephemIODC": 85,
                    "ephemL2Pflag": 0,
                    "ephemSF1Rsvd": {
                        "reserved1": 3427592,
                        "reserved2": 10711099,
                        "reserved3": 6590497,
                        "reserved4": 65266
                    },
                    "ephemTgd": 13,
                    "ephemToc": 13950,
                    "ephemAF2": 0,
                    "ephemAF1": -53,
                    "ephemAF0": -1226295,
                    "ephemCrs": -2069,
                    "ephemDeltaN": 13081,
                    "ephemM0": 488424951,
                    "ephemCuc": -1738,
                    "ephemE": 64044553,
                    "ephemCus": 1256,
                    "ephemAPowerHalf": 2701999468,
                    "ephemToe": 13950,
                    "ephemFitFlag": 0,
                    "ephemAODA": 31,
                    "ephemCic": -51,
                    "ephemOmegaA0": 1497574135,
                    "ephemCis": 55,
                    "ephemI0": 666068722,
                    "ephemCrc": 10905,
                    "ephemW": 576198844,
                    "ephemOmegaADot": -23947,
                    "ephemIDot": -1252
                }
            )
        }
        v["component"][1]["gps-AssistData"]["controlHeader"]["navigationModel"]["navModelList"].append(navModelList1)

        almanacList1 = {
            "satelliteID": 0,
            "almanacE": 15999,
            "alamanacToa": 99,
            "almanacKsii": 4699,
            "almanacOmegaDot": -673,
            "almanacSVhealth": 0,
            "almanacAPowerHalf": 10554624,
            "almanacOmega0": -5335843,
            "almanacW": 1638836,
            "almanacM0": 1638836,
            "almanacAF0": -44,
            "almanacAF1": -1
        }
        v["component"][1]["gps-AssistData"]["controlHeader"]["almanac"]["almanacList"].append(almanacList1)

        pdu = RRLP.RRLP_Messages.PDU
        pdu.set_val(v)
        print(pdu.to_asn1())
        print(pdu.to_uper())

    def generate_lpp_proto(self):
        pdu = LPP.LPP_PDU_Definitions.LPP_Message

        with open("lpp.dict", "w") as f:
            print(pdu.get_proto(), file=f)

    def generate_lppe_proto(self):
        pdu = LPPe.OMA_LPPE.OMA_LPPe_MessageExtension

        with open("lppe.dict", "w") as f:
            print(pdu.get_proto(), file=f)

    def test_lpp(self):
        pdu = LPP.LPP_PDU_Definitions.LPP_Message

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

        string = tx_data.hex()
        print("[Encoded][%d]: %s" % (len(string)/2, string))

    def test_encode_supl_start(self):
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

        self.encode_supl_message(message)

    def test_encode_supl_pos_init(self):
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

        self.encode_supl_message(message)

playground = Playground()
playground.test_encode_supl_pos_init()