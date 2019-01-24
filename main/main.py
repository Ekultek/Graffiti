
from lib.arguments import Parser
from lib.database import initialize


def main():
    opts = Parser().optparse()
    cursor = initialize(memory=opts.memoryDatabase)
    parsed_config = Parser().config_parser(opts)
    Parser().single_run_args(parsed_config, cursor)
