from pycrate_asn1dir import RRLP
from pycrate_asn1rt.utils import *

class RrlpSession:
    def encode_assit_data(self):
        rrlp_assit_data = {
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

        rrlp_assit_data["component"][1]["gps-AssistData"]["controlHeader"]["referenceTime"]["gpsTowAssist"].append(gpsTowAssit1)
        rrlp_assit_data["component"][1]["gps-AssistData"]["controlHeader"]["referenceTime"]["gpsTowAssist"].append(gpsTowAssit2)
        rrlp_assit_data["component"][1]["gps-AssistData"]["controlHeader"]["referenceTime"]["gpsTowAssist"].append(gpsTowAssit3)

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
        rrlp_assit_data["component"][1]["gps-AssistData"]["controlHeader"]["navigationModel"]["navModelList"].append(navModelList1)

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
        rrlp_assit_data["component"][1]["gps-AssistData"]["controlHeader"]["almanac"]["almanacList"].append(almanacList1)

        rrlp_pdu = RRLP.RRLP_Messages.PDU
        rrlp_pdu.set_val(rrlp_assit_data)
        return rrlp_pdu.to_uper()