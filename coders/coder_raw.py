from lib.database import insert_payload


class RawEncoder(object):

    payload_starts = {
        "powershell": "Powershell.exe -exec bypass IEX {}",
        "python": "python -c '{}'",
        "perl": "perl -e '{}'",
        "php": "php -r '{}'",
        "ruby": "ruby -e \"{}\"",
        "batch": "{}",
        "bash": "{}"
    }
    acceptable_exec_types = ("powershell", "php", "python", "perl", "ruby", "bash", "batch")

    def __init__(self, payload_data, cursor):
        self.payload = payload_data["data"]["payload"]
        self.exec_type = payload_data["data"]["information"]["exec"]
        self.payload_type = payload_data["data"]["information"]["type"]
        self.cursor = cursor

    def encode(self):
        if self.exec_type in self.acceptable_exec_types:
            payload = self.payload_starts[self.exec_type]
        else:
            payload = self.payload
        payload = payload.format(self.payload)
        is_inserted = insert_payload(payload, self.payload_type, self.exec_type, self.cursor)
        return payload, is_inserted
