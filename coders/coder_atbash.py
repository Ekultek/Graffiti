import string

from lib.database import insert_payload
from lib.settings import UnacceptableExecType


class AtbashEncoder(object):

    payload_starts = {
        "python": (
            "python -c "
            "'import string;a_l=string.ascii_letters;"
            "r_l=a_l[::-1];exec(\"\".join([r_l[a_l.index(c)] if c in r_l else c for c in \"{}\"]))'"
        )
    }
    acceptable_exec_types = ("python",)

    def __init__(self, payload_data, cursor):
        self.payload = payload_data["data"]["payload"]
        self.exec_type = payload_data["data"]["information"]["exec"]
        self.payload_type = payload_data["data"]["information"]["type"]
        self.cursor = cursor

    def atbash(self):
        all_letters = string.ascii_letters
        all_letters_reversed = all_letters[::-1]
        retval = []
        for c in list(self.payload):
            if c in all_letters:
                index = all_letters.index(c)
                c = all_letters_reversed[index]
            retval.append(c)
        return ''.join(retval)

    def encode(self):
        if self.exec_type in self.acceptable_exec_types:
            usable_payload = []
            for c in self.payload:
                if c == '"':
                    c = r'\"'
                usable_payload.append(c)
            self.payload = "".join(usable_payload)
            payload = self.payload_starts[self.exec_type]
        else:
            payload = ""
        if payload == "":
            raise UnacceptableExecType("{} cannot be encoded into atbash".format(self.exec_type))
        encoded_payload = self.atbash()
        retval = payload.format(encoded_payload)
        is_inserted = insert_payload(retval, self.payload_type, self.exec_type, self.cursor)
        return retval, is_inserted
