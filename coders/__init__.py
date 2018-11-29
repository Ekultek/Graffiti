from lib.settings import UnacceptableExecType
from coder_base64 import Base64Encoder
from coder_raw import RawCoder
from coder_hex import HexEncoder
from coder_xor import XorEncoder
from coder_rot13 import Rot13Encoder
from lib.jsonize import tuple_to_json


class Encoder(object):

    """
    encoder class that calls all the other encoder classes
    """

    def __init__(self, payload_data, cursor, lhost, lport, url, encode):
        self.payload = payload_data["data"]["payload"]
        self.exec_type = payload_data["data"]["information"]["exec"]
        self.payload_type = payload_data["data"]["information"]["type"]
        self.desc = payload_data["data"]["information"]["description"]
        self.ip = lhost
        self.port = lport
        self.url = url
        self.technique = encode
        self.cursor = cursor
        self.acceptable_encodings = {
            "xor": XorEncoder,
            "base64": Base64Encoder,
            "raw": RawCoder,
            "hex": HexEncoder,
            "rot13":  Rot13Encoder
        }

    def fix_payload(self):
        replacements = {
            "[IP]": self.ip,
            "[PORT]": self.port,
            "[URL]": self.url
        }
        for replace in replacements.keys():
            try:
                self.payload = str(self.payload).replace(replace, replacements[replace])
            except Exception:
                pass

    def encode(self):
        try:
            self.fix_payload()
            data = (self.desc, self.payload_type, self.exec_type, self.payload)
            json_data = tuple_to_json(data, sort_and_indent=False)
            retval = self.acceptable_encodings[self.technique](json_data, self.cursor).encode()
            return retval
        except UnacceptableExecType as e:
            print(e.message)
            return None
