import os
import json
import readline

import jsonize


class UnacceptableExecType(Exception): pass


class GraffitiCompleter(object):

    """
    complete the terminal commands class
    """

    def __init__(self, opts):
        self.opts = sorted(opts)
        self.possible_matches = []

    def complete_text(self, text, state):
        """
        do an auto complete of the terminal command
        """
        if state == 0:
            if text:
                self.possible_matches = [m for m in self.opts if m and m.startswith(text)]
            else:
                self.possible_matches = self.opts[:]
        try:
            return self.possible_matches[state]
        except IndexError:
            return None


# current working directory
CUR_DIR = os.getcwd()

# path to where the history will be stored
HISTORY_FILES_PATH = "{}/.history".format(CUR_DIR)

# path to where the configuration file is stored
CONFIG_PATH = "{}/conf.json".format(CUR_DIR)

# path to where all the payloads are stored
PAYLOADS_PATH = "{}/etc/payloads".format(CUR_DIR)

# path to the database file
DATABASE_PATH = "{}/graffiti.db".format(CUR_DIR)

# template to finish the payloads when they are displayed
FINISH_PATH_TEMPLATE = "{}/etc/payloads{}"

# version number
VERSION = "0.0.10"

# sexy ass banner
BANNER = """\033[30m
  ________              _____  _____.__  __  .__ 
 /  _____/___________ _/ ____\/ ____\__|/  |_|__|
/   \  __\_  __ \__  \\\\   __\\\\   __\|  \   __\  |
\    \_\  \  | \// __ \|  |   |  |  |  ||  | |  |
 \______  /__|  (____  /__|   |__|  |__||__| |__|
        \/           \/           
 v({})               
\033[0m""".format(VERSION)

# help message for the terminal
TERMINAL_HELP_MESSAGE = """
 Command                                  Description
---------                                --------------
 help/?                                  Show this help
 external                                List available external commands
 cached/stored                           Display all payloads that are already in the database
 list/show                               List all available payloads
 search <phrase>                         Search for a specific payload
 use <payload> <coder>                   Use this payload and encode it using a specified coder
 info                                    Get information on all the payloads
 check                                   Check for updates
 history/mem[ory]                        Display command history
 exit/quit                               Exit the terminal and running session
 encode <script-type> <coder>            Encode a provided payload
 check                                   Check for updates
"""


def complete(keywords):
    """
    from a list of given commands, we can complete them using tab
    """
    self_completer = GraffitiCompleter(keywords)
    readline.set_completer(self_completer.complete_text)
    readline.parse_and_bind('tab: complete')


def get_payload_paths(is_list=False):
    """
    get all the paths to the available payloads
    """
    if not is_list:
        retval = {}
        available_payloads = []
        for path, _, files in os.walk(PAYLOADS_PATH):
            for name in [f for f in files if f.endswith(".json")]:
                available_payloads.append(os.path.join(path, name))
        for path in available_payloads:
            os_specific = path.split("payload")[-1].split("/")[1]
            retval[os_specific] = []
        for path in available_payloads:
            path = path.split("payloads")[-1]
            os_type = path.split("/")[1]
            retval[os_type].append(path)
    else:
        retval = []
        available_payloads = []
        for path, _, files in os.walk(PAYLOADS_PATH):
            for name in [f for f in files if f.endswith(".json")]:
                available_payloads.append(os.path.join(path, name))
        for path in available_payloads:
            path = path.split("payloads")[-1]
            retval.append(path)
    return retval


def get_single_payload(path):
    """
    grab a single payload
    """
    with open(path) as data:
        return json.load(data)


def prepare_single_payload(payload, script_type, exec_type=None, description=None):
    """
    prepare a single payload for encoding
    """
    tuple_data = (description, script_type, exec_type, payload)
    json_data = jsonize.tuple_to_json(tuple_data, sort_and_indent=False)
    return json_data


def rewrite_config():
    """
    rewrite the config at the exit of the program
    """
    data = {
        "graffiti": {
            "codecToUse": "",
            "createNewPayloadPath": "",
            "createPayloadFile": "",
            "listAvailablePayloads": "",
            "payloadPathToUse": "",
            "userDefinedPayload": "",
            "userDefinedLhost": "",
            "userDefinedLport": "",
            "userDefinedURL": "",
            "viewCached": "",
            "useTerminal": False,
            "saveCommandHistory": "",
            "wipeData": False,
            "moreExternalCommands": "",
            "viewAvailableCodecs": False
        }
    }
    with open(CONFIG_PATH, "w") as conf:
        json.dump(data, conf, sort_keys=True, indent=True)


def check_payload(payload):
    """
    check the payload to determine if there is anything that needs to be added
    """
    import re

    checkers = {
        "LHOST": "[IP]",
        "LPORT": "[PORT]",
        "URL": "[URL]"
    }
    missing = []
    for item in checkers.keys():
        searcher = re.compile(checkers[item])
        if searcher.search(payload) is not None:
            missing.append(item)
    return missing


def close(exit_code=0):
    """
    close the program
    """
    rewrite_config()
    exit(exit_code)


def find_similar(command, internal, external):
    """
    find commands that are similar to the one used
    """
    retval = []
    for internal, external in zip(internal, external):
        first_char = command[0]
        if str(internal).startswith(first_char):
            retval.append(internal)
        if str(external).startswith(first_char):
            retval.append(external)
    return retval


def display_payload(payload):
    print(payload)


def get_history_files(path):
    """
    grab all the paths to the history files
    """
    retval = []
    for dirpath, _, files in os.walk(path):
        for f in files:
            retval.append(os.path.abspath(os.path.join(dirpath, f)))
    return retval


def secure_delete(path, passes=3):
    """
    securely delete a file by running passes through it
    """
    import struct
    import string
    import random

    length = os.path.getsize(path)
    data = open(path, "w")

    for _ in range(passes):
        data.seek(0)
        data.write(''.join(random.choice(string.printable) for _ in range(length)))
    for _ in range(passes):
        data.seek(0)
        data.write(os.urandom(length))
    for _ in range(passes):
        data.seek(0)
        data.write(struct.pack("B", 0) * length)
    data.close()
    os.remove(path)


def create_external_commands():
    """
    create external commands that can be used, i added a few that i thought would
    be useful
    """
    retval = set(os.listdir("/bin"))
    useful_commands = (
        "clear", "ssh",
        "hashcat", "rsync",
        "nmap", "find",
        "ifconfig", "grep",
        "vi", "telnet",
        "ftp", "bash",
        "python", "nc"
    )
    for command in useful_commands:
        retval.add(command)
    return list(retval)


def tails(file_object, last_lines=50):
    """
    return the last `n` lines of a file, much like the Unix
    tails command
    """
    with open(file_object) as file_object:
        assert last_lines >= 0
        pos, lines = last_lines+1, []
        while len(lines) <= last_lines:
            try:
                file_object.seek(-pos, 2)
            except IOError:
                file_object.seek(0)
                break
            finally:
                lines = list(file_object)
            pos *= 2
    return "".join(lines[-last_lines:])


def get_encoders(is_view_all=False):
    """
    get the possible encoding techniques from the coders directory
    :return:
    """
    path = "{}/coders".format(CUR_DIR)
    bad = (".pyc", "__init__.py")
    retval = []
    for c in os.listdir(path):
        if not any(b in c for b in bad):
            retval.append(c.split("_")[-1].split(".")[0])
    if is_view_all:
        from coders import Encoder

        retval = Encoder(None, None, None, None, None, None, get_encoders=True)
    return retval

