# ~*~ coding:utf-8 ~*~

from string import ascii_letters
from random import choice
from itertools import (
    cycle,
    izip
)

from lib.database import insert_payload
from lib.settings import UnacceptableExecType


class XorEncoder(object):

    payload_starts = {
        "python": "python -c 'print \"\".join([chr(ord(c)^ord(k) for c,k in zip(\"{}\",\"{}\")'",
        "php": (
            "php -r '$output=\"\";$key={};"
            "$text={};for($i=0;$i<strlen($text);$i++){{"
            "for($j=0;($j<strlen($key) && $i<strlen($text));$j++,$i++){{"
            "$output .= $text{{$i}} ^ $key{{$j}};}}}}}};exec($output);'"
        ),

    }
    acceptable_exec_types = ("php", "python")

    def __init__(self, payload_data, cursor):
        self.payload = payload_data["data"]["payload"]
        self.exec_type = payload_data["data"]["information"]["exec"]
        self.payload_type = payload_data["data"]["information"]["type"]
        self.cursor = cursor

    @staticmethod
    def random_pass():
        length = 10
        retval = []
        for _ in range(length):
            retval.append(choice(ascii_letters))
        return ''.join(retval)

    def xor_string(self):
        encrypt_pass = self.random_pass()
        ciphered = ''.join(chr(ord(c) ^ ord(k)) for c, k in izip(self.payload, cycle(encrypt_pass)))
        return ciphered, encrypt_pass

    def encode(self):
        data = self.xor_string()
        encoded_payload, key = data
        if self.exec_type in self.acceptable_exec_types:
            payload = self.payload_starts[self.exec_type]
        else:
            payload = ""
        if payload == "":
            raise UnacceptableExecType("{} is unable to be encrypted into xor".format(self.exec_type))
        payload = payload.format(encoded_payload, key)
        is_inserted = insert_payload(payload, self.payload_type, self.exec_type, self.cursor)
        return payload, is_inserted
