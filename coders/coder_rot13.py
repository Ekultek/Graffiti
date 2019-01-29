from lib.database import insert_payload
from lib.settings import UnacceptableExecType


class Rot13Encoder(object):

    payload_starts = {
        "python": "python -c 'exec(\"{}\".decode(\"rot13\"))'",
        "ruby": "ruby -e \"str='{}';eval(str.tr 'A-Za-z', 'N-ZA-Mn-za-m')\"",
        "php": "php -r '$string=str_rot13(\"{}\");'"
    }
    acceptable_exec_types = ("python", "ruby", "php")

    def __init__(self, payload_data, cursor):
        self.payload = payload_data["data"]["payload"]
        self.exec_type = payload_data["data"]["information"]["exec"]
        self.payload_type = payload_data["data"]["information"]["type"]
        self.cursor = cursor

    def encode(self):
        tmp = []
        for char in list(self.payload):
            if char == '"':
                char = r'\"'
            tmp.append(char)
        usable_payload = "".join(tmp)
        encoded_payload = usable_payload.encode("rot13")
        if self.exec_type.lower() in self.acceptable_exec_types:
            payload = self.payload_starts[self.exec_type]
        else:
            payload = ""
        if payload == "":
            raise UnacceptableExecType("# {} is not able to be encoded into Rot13".format(self.exec_type))

        retval = payload.format(encoded_payload)
        is_inserted = insert_payload(retval, self.payload_type, self.exec_type, self.cursor)
        return retval, is_inserted
