from lib.settings import UnacceptableExecType
from coder_base64 import Base64Encoder
from coder_raw import RawEncoder
from coder_hex import HexEncoder
from coder_xor import XorEncoder
from coder_rot13 import Rot13Encoder
from coder_atbash import AtbashEncoder
from coder_aes256 import AESEncoder
from lib.jsonize import tuple_to_json


class Encoder(object):

    """
    encoder class that calls all the other encoder classes
    """

    # needs to be here for a dirty little hack
    acceptable_encodings = ()

    def __init__(self, payload_data, cursor, lhost, lport, url, encode, get_encoders=False):
        self.acceptable_encodings = {
            "xor": XorEncoder,
            "base64": Base64Encoder,
            "raw": RawEncoder,
            "hex": HexEncoder,
            "rot13": Rot13Encoder,
            "atbash": AtbashEncoder,
            "aes256": AESEncoder
        }
        if not get_encoders:
            self.payload = payload_data["data"]["payload"]
            self.exec_type = payload_data["data"]["information"]["exec"]
            self.payload_type = payload_data["data"]["information"]["type"]
            self.desc = payload_data["data"]["information"]["description"]
            self.ip = lhost
            self.port = lport
            self.url = url
            self.technique = encode
            self.cursor = cursor
        else:
            self.retval = {}
            for item in self.acceptable_encodings.keys():
                self.retval[item] = self.acceptable_encodings[item].acceptable_exec_types
            self.return_encoders()

    def return_encoders(self):
        return self.retval

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
