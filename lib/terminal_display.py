import re
import os
import json
import subprocess
from datetime import date

from coders import Encoder
from lib.settings import (
    complete,
    TERMINAL_HELP_MESSAGE,
    FINISH_PATH_TEMPLATE,
    CUR_DIR,
    get_single_payload,
    UnacceptableExecType,
    prepare_single_payload,
    close,
    find_similar,
    display_payload,
    create_external_commands,
    tails,
    get_encoders
)


try:
    raw_input
except:
    raw_input = input


class GraffitiTerminal(object):

    """
    terminal display object, sets an interactive terminal object
    """

    # available internal terminal commands
    terminal_commands = [
        "search", "list", "show",
        "use", "info", "history",
        "exit", "quit", "?", "help",
        "check", "cached", "encode",
        "external", "mem", "memory",
        "stored"
    ]
    # available external terminal commands that are taken out of the `/bin` folder
    # I also added some other commands that i thought would be useful, you can also
    # add your own by passing the `-mC` flag and providing a list of commands
    # separated by a space
    available_external_commands = create_external_commands()

    def __init__(self, cached_payloads, available_payloads, cursor):
        self.cache = cached_payloads
        self.available = available_payloads
        self.terminal_start = "\033[32mroot\033[0m@\033[35mgraffiti\033[0m:\033[30m~/graffiti\033[0m# "
        self.history = []
        self.quit_terminal = False
        self.help = TERMINAL_HELP_MESSAGE
        self.clean_exit_code = 1
        self.cursor = cursor
        self.history_dir = "{}/.history/{}".format(CUR_DIR, str(date.today()))
        self.full_history_file_path = "{}/graffiti.history".format(self.history_dir)

    def reflect_memory(self):
        """
        reflect the history back into the command history, this way
        we can remember all the history from the day
        """
        def random_file_ext():
            retval = []
            for _ in range(5):
                retval.append(random.choice(string.ascii_letters))
            return "".join(retval)

        if os.path.exists(self.history_dir):
            tmp = []
            with open(self.full_history_file_path) as history:
                for item in history.readlines():
                    tmp.append(item.strip())
            if len(tmp) > 200:
                import shutil
                import random
                import string

                history_file_backup = self.full_history_file_path + ".{}.old".format(random_file_ext())
                shutil.copy(
                    self.full_history_file_path, history_file_backup
                )
                open(self.full_history_file_path, "w").close()
                print("history file to large, old file saved under '{}'".format(history_file_backup))
            else:
                for item in tmp:
                    self.history.append(item)

    def get_choice(self):
        """
        get the users choice and return it
        """
        original_choice = raw_input("{}".format(self.terminal_start))
        try:
            check_choice = original_choice.split(" ")[0]
        except:
            check_choice = original_choice
        if check_choice in self.available_external_commands:
            return "external", original_choice
        elif check_choice in self.terminal_commands:
            return "local", original_choice
        else:
            return "unknown", original_choice

    def do_terminal_command(self, command):
        """
        run a external terminal command from this terminal
        """
        self.history.append(command)
        try:
            proc = subprocess.call(command, shell=True)
            if not proc:
                return None
            return proc
        except KeyboardInterrupt:
            print("user quit before command could finish")
            return None
        except Exception:
            return None

    def do_display_help(self):
        """
        display the help menu
        """
        print(self.help)

    def do_display_command_history(self):
        """
        display the command history of the terminal
        """
        if len(self.history) > 100:
            truncacted_history = tails(self.full_history_file_path)
            print(truncacted_history)
            print("history truncated to last 50 lines")
        else:
            for i, item in enumerate(self.history, start=1):
                if len(list(str(i))) == 2:
                    spacer1, spacer2 = "  ", "   "
                elif len(list(str(i))) == 3:
                    spacer1, spacer2 = " ", "   "
                else:
                    spacer1, spacer2 = "   ", "   "
                print("{}{}{}{}".format(spacer1, i, spacer2, item))

    def do_display_cached(self):
        """
        display the payloads already encoded in the database
        """
        if len(self.cache) != 0:
            for item in self.cache:
                _, payload, payload_type, exec_type = item
                print("\nType: {}\nExecution: {}\nPayload: {}".format(
                    payload_type.title(), exec_type.title(), str(repr(payload)))
                )
        else:
            print("no cached payloads in database")

    def do_display_available(self):
        """
        display the available payloads
        """
        for item in self.available:
            print(item)

    def do_use_payload(self, selected, encoder):
        """
        use a selected payload, encode it, and stash it in a database for future use
        """
        encoders = get_encoders()
        selected_choice = False
        if encoder in encoders:
            choice = encoders.index(encoder)
        else:
            print("invalid encoding or no encoding given, defaulting to base64")
            choice = 0
        while not selected_choice:
            try:
                technique = encoders[int(choice)]
                payload_path = FINISH_PATH_TEMPLATE.format(CUR_DIR, selected)
                payload_data = get_single_payload(payload_path)
                if payload_data["data"]["information"]["type"].lower() == "dropper":
                    usable_data = {"url": raw_input("enter the URL to connect to: "), "lhost": None, "lport": None}
                elif payload_data["data"]["information"]["type"].lower() == "enum":
                    usable_data = {"url": raw_input("enter the domain to enumerate: "), "lhost": None, "lport": None}
                elif payload_data["data"]["information"]["type"].lower() in ("reverse", "bind"):
                    usable_data = {
                        "url": None, "lhost": raw_input("enter the LHOST: "), "lport": raw_input("enter the LPORT: ")
                    }
                else:
                    usable_data = {
                        "url": None,
                        "lhost": None,
                        "lport": None
                    }
                encoded = Encoder(
                    payload_data,
                    self.cursor,
                    usable_data["lhost"],
                    usable_data["lport"],
                    usable_data["url"],
                    technique
                ).encode()
                selected_choice = True
                return encoded
            except TypeError:
                print("invalid selection")
            except UnacceptableExecType as e:
                print(e.message)
                return None

    def do_search(self, text):
        """
        search for a specific payload
        """
        searcher = re.compile(text)
        retval = []
        for item in self.available:
            if searcher.search(item) is not None:
                retval.append(item)
        return retval

    def do_display_info(self):
        """
        display all the information on the payloads
        """
        for path in self.available:
            full_path = FINISH_PATH_TEMPLATE.format(CUR_DIR, path)
            with open(full_path) as f:
                data = json.load(f)
                print("\nScript type: {}\nExecution type: {}\nInformation: {}\nFull path: {}".format(
                    data["data"]["information"]["exec"],
                    data["data"]["information"]["type"],
                    data["data"]["information"]["description"],
                    full_path
                ))

    def do_encode_payload(self, payload, script_type, encoder, description, execution_type):
        """
        encode a personal payload
        """
        prepared_payload = prepare_single_payload(
            payload, execution_type, exec_type=script_type, description=description
        )
        required_arguments = ("lhost", "lport", "url")
        args = {}
        for argument in required_arguments:
            args[argument] = raw_input("enter the {} (enter for None): ".format(argument.upper()))
        encoded = Encoder(
            prepared_payload, self.cursor,
            args["lhost"], args["lport"], args["url"], encoder
        ).encode()
        return encoded

    def do_list_external_commands(self):
        print(" ".join(self.available_external_commands))

    def do_exit(self, save_history):
        """
        exit the terminal, saving history if the save_history flag is set to True
        """
        self.quit_terminal = True
        if save_history:
            if not os.path.exists(self.history_dir):
                os.makedirs(self.history_dir)
            print("saving current history to a file")
            with open(self.full_history_file_path, "a+") as data:
                for item in self.history:
                    data.write(item + "\n")
            print("exiting terminal")

    def do_check(self):
        """
        check for updates
        """
        subprocess.call(["git", "pull", "origin", "master"])

    def do_start(self, save_history, more_commands=None):
        """
        drop into the terminal and begin
        """
        if more_commands is not None:
            for com in more_commands:
                self.available_external_commands.append(com)
        self.reflect_memory()
        seperator = "-" * 30
        try:
            while not self.quit_terminal:
                complete(self.terminal_commands)
                try:
                    choice_type, choice = self.get_choice()
                    if choice_type == "unknown":
                        similar_commands = find_similar(choice, self.terminal_commands, self.available_external_commands)
                        if len(similar_commands) != 0:
                            if len(similar_commands) > 1:
                                output = (
                                    "no command '{}' found, but there are {} similar commands\n"
                                    "{}: command not found".format(
                                        choice, len(similar_commands),  choice
                                    )
                                )
                            else:
                                output = (
                                    "no command '{}' found, but there is {} similiar command\n"
                                    "{}: command not found".format(
                                        choice, len(similar_commands), choice
                                    )
                                )
                        else:
                            output = "{}: command not found".format(choice)
                        print(output)
                        self.history.append(choice)
                    elif choice_type == "external":
                        self.do_terminal_command(choice)
                    else:
                        self.history.append(choice)
                        choice = choice.lower()
                        try:
                            choice_data = choice.split(" ")
                        except:
                            choice_data = None
                        if any(c == choice for c in ["help", "?"]):
                            self.do_display_help()
                        elif any(c == choice for c in ["list", "show"]):
                            self.do_display_available()
                        elif any(c == choice for c in ["cached", "stored"]):
                            self.do_display_cached()
                        elif choice == "external":
                            self.do_list_external_commands()
                        elif any(c == choice for c in ["history", "mem", "memory"]):
                            self.do_display_command_history()
                        elif "use" in choice:
                            if len(choice_data) != 3:
                                print("must specify a payload and an encoding technique ({})".format(
                                    ", ".join(get_encoders())
                                ))
                            else:
                                encoded_payload = self.do_use_payload(choice_data[1], choice_data[-1])
                                if encoded_payload is not None:
                                    display_payload(encoded_payload[0])
                        elif "search" in choice:
                            if len(choice_data) != 2:
                                print("must specify what to search for (IE search windows)")
                            else:
                                found = self.do_search(choice_data[1])
                                if len(found) == 0:
                                    print("did not find any relevant options")
                                else:
                                    print("found {} relevant options:\n{}".format(len(found), seperator))
                                    for item in found:
                                        print(item)
                        elif choice == "check":
                            self.do_check()
                        elif choice == "info":
                            self.do_display_info()
                        elif "encode" in choice:
                            if len(choice_data) < 3:
                                print(
                                    "must specify a few things first: "
                                    "encode <script_type> <coder> [<description> <execution_type>]"
                                )
                            else:
                                payload = raw_input("enter your payload: ")
                                script_type = choice_data[1]
                                encoder = choice_data[2]
                                try:
                                    description = choice_data[3]
                                except IndexError:
                                    description = None
                                try:
                                    exec_type = choice_data[4]
                                except IndexError:
                                    exec_type = None
                                encoded = self.do_encode_payload(payload, script_type, encoder, description, exec_type)
                                display_payload(encoded[0])
                        elif choice == "exit" or choice == "quit":
                            self.do_exit(save_history)
                except IndexError:
                    pass
            if self.quit_terminal:
                close(exit_code=self.clean_exit_code)
        except KeyboardInterrupt:
            self.do_exit(save_history)
            close()
