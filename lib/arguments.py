import json
import string
from argparse import ArgumentParser

from coders import Encoder
from lib.terminal_display import GraffitiTerminal
from lib.database import (
    fetch_cached_payloads,
    insert_payload
)
from lib.jsonize import (
    tuple_to_json,
    write_to_file
)
from lib.settings import (
    CONFIG_PATH,
    get_payload_paths,
    close, CUR_DIR,
    prepare_single_payload,
    check_payload,
    get_single_payload,
    FINISH_PATH_TEMPLATE,
    display_payload,
    secure_delete,
    HISTORY_FILES_PATH,
    DATABASE_PATH,
    get_history_files,
    BANNER,
    get_encoders
)


class Parser(ArgumentParser):

    """
    argument parser class
    """

    def __init__(self):
        super(Parser, self).__init__()

    @staticmethod
    def optparse():
        """
        where we parse all our arguments
        """
        parser = ArgumentParser()
        parser.add_argument(
            "-c", "--codec", metavar="CODEC", choices=get_encoders(), dest="codecToUse",
            help="specify an encoding technique (*default=None)", default=None
        )
        parser.add_argument(
            "-p", "--payload", metavar="PAYLOAD", dest="payloadPathToUse",
            help="pass the path to a payload to use (*default=None)", default=None
        )
        parser.add_argument(
            "--create", metavar=("PAYLOAD", "SCRIPT-TYPE", "PAYLOAD-TYPE", "DESCRIPTION", "OS"), nargs=5,
            dest="createPayloadFile",
            help="create a payload file and store it inside of ./etc/payloads (*default=None)",
            default=None
        )
        parser.add_argument(
            "-l", "--list", action="store_true", dest="listAvailablePayloads",
            help="list all available payloads by path (*default=False)", default=False
        )
        parser.add_argument(
            "-P", "--personal-payload", metavar=("PAYLOAD", "SCRIPT-TYPE,PAYLOAD-TYPE,DESCRIPTION"), nargs="*",
            default=None, dest="userDefinedPayload",
            help="pass your own personal payload to use for the encoding (*default=None)"
        )
        parser.add_argument(
            "-lH", "--lhost", dest="userDefinedLhost", metavar="LISTENING-ADDRESS", default=None,
            help="pass a listening address to use for the payload (if needed) (*default=None)"
        )
        parser.add_argument(
            "-lP", "--lport", dest="userDefinedLport", metavar="LISTENING-PORT", default=None,
            help="pass a listening port to use for the payload (if needed) (*default=None)"
        )
        parser.add_argument(
            "-u", "--url", dest="userDefinedURL", metavar="URL", default=None,
            help="pass a URL if needed by your payload (*default=None)"
        )
        parser.add_argument(
            "-vC", "--view-cached", action="store_true", default=False, dest="viewCached",
            help="view the cached data already present inside of the database"
        )
        parser.add_argument(
            "-H", "--no-history", action="store_false", default=True, dest="saveCommandHistory",
            help="do not store the command history (*default=True)"
        )
        parser.add_argument(
            "-W", "--wipe", action="store_true", default=False, dest="wipeData",
            help="wipe the database and the history (*default=False)"
        )
        parser.add_argument(
            "--memory", action="store_true", default=False, dest="memoryDatabase",
            help="initialize the database into memory instead of a .db file (*default=False)"
        )
        parser.add_argument(
            "-mC", "--more-commands", default=None, dest="moreExternalCommands",
            nargs="+", metavar=("COMMAND", "COMMAND"),
            help="pass more external commands, this will allow them to be accessed inside of the terminal "
                 "commands must be in your PATH (*default=None)"
        )
        parser.add_argument(
            "-Vc", "--view-codecs", default=False, dest="viewAvailableCodecs", action="store_true",
            help="view the current available encoding codecs and their compatible languages"
        )
        return parser.parse_args()

    @staticmethod
    def config_parser(opts):
        """
        creates the configuration from the parser
        """
        with open(CONFIG_PATH) as conf:
            is_single_arg = []
            data = json.load(conf)
            if opts.listAvailablePayloads:
                data["graffiti"]["listAvailablePayloads"] = True
                is_single_arg.append(len(is_single_arg))
            if opts.wipeData:
                data["graffiti"]["wipeData"] = True
                is_single_arg.append(len(is_single_arg))
            if opts.viewCached:
                data["graffiti"]["viewCached"] = True
                is_single_arg.append(len(is_single_arg))
            if opts.createPayloadFile is not None:
                data["graffiti"]["createPayloadFile"] = opts.createPayloadFile
                is_single_arg.append(len(is_single_arg))
            if opts.codecToUse is not None:
                data["graffiti"]["codecToUse"] = opts.codecToUse
                is_single_arg.append("1")
            if opts.payloadPathToUse is not None:
                data["graffiti"]["payloadPathToUse"] = opts.payloadPathToUse
                is_single_arg.append(len(is_single_arg))
            if opts.userDefinedPayload is not None:
                data["graffiti"]["userDefinedPayload"] = opts.userDefinedPayload
                is_single_arg.append(len(is_single_arg))
            if opts.userDefinedLport is not None:
                data["graffiti"]["userDefinedLport"] = opts.userDefinedLport
                is_single_arg.append(len(is_single_arg))
            if opts.userDefinedLhost is not None:
                data["graffiti"]["userDefinedLhost"] = opts.userDefinedLhost
                is_single_arg.append(len(is_single_arg))
            if opts.viewAvailableCodecs:
                data["graffiti"]["viewAvailableCodecs"] = opts.viewAvailableCodecs
                is_single_arg.append(len(is_single_arg))
            if opts.userDefinedURL is not None:
                data["graffiti"]["userDefinedURL"] = opts.userDefinedURL
                is_single_arg.append("1")
            if len(is_single_arg) == 0:
                data["graffiti"]["saveCommandHistory"] = opts.saveCommandHistory
                data["graffiti"]["useTerminal"] = True
                data["graffiti"]["moreExternalCommands"] = opts.moreExternalCommands
            return data

    @staticmethod
    def single_run_args(conf, cursor):
        """
        parses the configuration file and tells the program what needs to be done
        """
        # fetch the cached payloads out of the database
        cached_payloads = fetch_cached_payloads(cursor)
        if conf["graffiti"]["wipeData"]:
            print("wiping the database and the history files")
            secure_delete(DATABASE_PATH)
            history_files = get_history_files(HISTORY_FILES_PATH)
            for f in history_files:
                secure_delete(f)
            print("database and history files wiped")
            close()
        if conf["graffiti"]["useTerminal"]:
            print(BANNER)
            print(
                "no arguments have been passed, dropping into terminal type `help/?` to get help, "
                "all commands that sit inside of `/bin` are available in the terminal"
            )
            available_payloads = get_payload_paths(is_list=True)
            GraffitiTerminal(
                cached_payloads, available_payloads, cursor
            ).do_start(conf["graffiti"]["saveCommandHistory"])
            exit()
        if conf["graffiti"]["viewAvailableCodecs"]:
            codecs = get_encoders(is_view_all=True).return_encoders()
            print("\033[4mCODEC:\033[0m\t\t\033[4mACCEPTABLE:\033[0m")
            for item in codecs.keys():
                print("{}\t\t{}".format(item, ','.join(codecs[item])))
            close()
        if conf["graffiti"]["listAvailablePayloads"]:
            available_payloads = get_payload_paths()
            for os_spec in available_payloads.keys():
                print("\n\033[4m{} payloads:\033[0m\n".format(os_spec.title()))
                for payload in available_payloads[os_spec]:
                    print(payload)
            close()
        if conf["graffiti"]["viewCached"]:
            print("total of {} payloads present".format(len(cached_payloads)))
            for cache in cached_payloads:
                non_chars = False
                if any(c not in string.printable for c in cache[1]):
                    non_chars = True
                print(
                    "\nLanguage: {}\nPayload Type: {}\nPayload: {}".format(
                        cache[-1], cache[-2], str(cache[1]) if not non_chars else str(repr(cache[1]))
                    )
                )
            close()
        if conf["graffiti"]["codecToUse"] != "":
            if conf["graffiti"]["userDefinedPayload"] != "":
                data = conf["graffiti"]["userDefinedPayload"]
                if len(data) < 2:
                    print("must provide at least the payload and the language type")
                    close(exit_code=1)
                else:
                    if len(data) == 4:
                        retval = prepare_single_payload(
                            data[0], data[2], exec_type=data[1], description=data[-1]
                        )
                    elif len(data) == 3:
                        retval = prepare_single_payload(
                            data[0], data[2], exec_type=data[1], description="N/A"
                        )
                    else:
                        retval = prepare_single_payload(
                            data[0], "N/A", exec_type=data[1], description="N/A"
                        )
                    checks = check_payload(data[0])
                    if len(checks) != 0:
                        print(
                            "seems you did not provide needed data to prepare your payload, you need to pass {}. "
                            "either pass the data using the host commands, add the data to the payload, "
                            "or remove the data from the payload all together".format(
                                ",".join(checks)
                            )
                        )
                        close(exit_code=1)
                    else:
                        if str(conf["graffiti"]["codecToUse"]) == "":
                            print("must specify a codec to use")
                            close(exit_code=1)
                        encoded = Encoder(
                            retval, cursor,
                            conf["graffiti"]["userDefinedLhost"],
                            conf["graffiti"]["userDefinedLport"],
                            conf["graffiti"]["userDefinedURL"],
                            conf["graffiti"]["codecToUse"]
                        ).encode()
                        print(encoded[0])
                        close()
            elif conf["graffiti"]["payloadPathToUse"] != "":
                useable_payload_paths = get_payload_paths(is_list=True)
                if conf["graffiti"]["payloadPathToUse"] in useable_payload_paths:
                    full_path = FINISH_PATH_TEMPLATE.format(CUR_DIR, conf["graffiti"]["payloadPathToUse"])
                    data_json = get_single_payload(full_path)
                    payload_type = data_json["data"]["information"]["type"]
                    if payload_type == "reverse":
                        if conf["graffiti"]["userDefinedLhost"].isspace() or conf["graffiti"]["userDefinedLport"] == "":
                            print("no LHOST or LPORT given, specify and try again")
                            close()
                        else:
                            graph_data = (conf["graffiti"]["userDefinedLhost"], conf["graffiti"]["userDefinedLport"], None)
                    elif payload_type == "dropper":
                        if conf["graffiti"]["userDefinedURL"] == "":
                            print("no URL specified for the dropper, specify one and try again")
                            close()
                        else:
                            graph_data = (None, None, conf["graffiti"]["userDefinedURL"])
                    elif payload_type == "enum":
                        if conf["graffiti"]["userDefinedURL"] == "":
                            print("no domain specified for the enumeration, specify one and try again")
                            close()
                        else:
                            graph_data = (None, None, conf["graffiti"]["userDefinedURL"])
                    else:
                        graph_data = (None, None, None)
                    encoded_payload = Encoder(
                        data_json, cursor, graph_data[0], graph_data[1], graph_data[2], conf["graffiti"]["codecToUse"]
                    ).encode()
                    if encoded_payload is not None:
                        display_payload(encoded_payload[0])
                    else:
                        print("# dumping raw encoded payload")
                        encoded_payload = Encoder(
                            data_json, cursor, graph_data[0], graph_data[1], graph_data[2], "raw"
                        ).encode()
                        display_payload(encoded_payload[0])
                    close()
                else:
                    print("unknown payload path, do you want to make a payload?")
                    close()
        if conf["graffiti"]["createPayloadFile"] != "":
            acceptable_operating_systems = ["windows", "linux", "mac", "unix", "shared"]
            if conf["graffiti"]["createPayloadFile"][-1] in acceptable_operating_systems:
                target_system_type = conf["graffiti"]["createPayloadFile"][-1]
                description = conf["graffiti"]["createPayloadFile"][-2]
                payload_type = conf["graffiti"]["createPayloadFile"][-3]
                execution_type = conf["graffiti"]["createPayloadFile"][1]
                usable_payload = conf["graffiti"]["createPayloadFile"][0]
                data = (description, payload_type, execution_type, usable_payload)
                json_data = tuple_to_json(data)
                path = write_to_file(json_data, target_system_type, execution_type, payload_type)
                database_info = tuple_to_json(data, sort_and_indent=False)
                insert_payload(database_info, payload_type, execution_type, cursor)
                print("payload created and stored in {}".format(path))
                close()
            else:
                print("please choose an OS from the following and try again: {}".format(
                    ",".join(acceptable_operating_systems))
                )
                close()
        close()
