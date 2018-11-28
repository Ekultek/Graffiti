import os
import json
from random import choice
from string import ascii_letters

import lib.settings


def generate_filename(_os, lang, exec_type, indicator_length=5):
    """
    generate a filename from given data
    """
    indicator = "".join(choice(ascii_letters) for _ in range(indicator_length))
    return "{}_{}_{}_{}.json".format(exec_type.replace(" ", "_"), _os, lang, indicator)


def tuple_to_json(data, sort_and_indent=True):
    """
    turn a tuple into a JSON dict
    """
    assert type(data) == tuple
    assert len(data) == 4
    retval = {"data": {"information": {}, "payload": ""}}
    retval["data"]["information"]["description"] = data[0]
    retval["data"]["information"]["type"] = data[1]
    retval["data"]["information"]["exec"] = data[2]
    retval["data"]["payload"] = data[3]
    if sort_and_indent:
        return json.dumps(retval, sort_keys=True, indent=True)
    else:
        return retval


def write_to_file(to_write, indicator=None, script_type=None, exec_type=None):
    """
    write the data to a JSON file
    """
    if exec_type is None or exec_type == "":
        exec_type = "unknown"
    if indicator is None or indicator == "":
        indicator = "user_defined"
    if script_type is None or script_type == "":
        script_type = "unknown"
    filename = generate_filename(indicator, script_type, exec_type)
    file_path = "{}/{}/{}".format(lib.settings.PAYLOADS_PATH, indicator, script_type)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = "{}/{}".format(file_path, filename)
    with open(file_path, "a+") as f:
        f.write(to_write)
    return file_path
