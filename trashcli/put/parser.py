import os
import pprint
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
from typing import NamedTuple, Any, Union, List, Optional

from trashcli.shell_completion import TRASH_DIRS, TRASH_FILES, add_argument_to
from trashcli.trash import version

mode_force = 'force'
mode_interactive = 'interactive'

ExitWithCode = NamedTuple('ExitWithCode', [
    ('type', type),
    ('exit_code', int),
])

Trash = NamedTuple('Trash', [
    ('type', type),
    ('program_name', str),
    ('options', Any),
    ('files', List[str]),
    ('trash_dir', Optional[str]),
    ('mode', str),
    ('forced_volume', Optional[str]),
    ('verbose', int),
    ('home_fallback', bool),
])


class Parser:

    def parse_args(self, argv):  # type: (list) -> Union[ExitWithCode, Trash]
        program_name = os.path.basename(argv[0])
        arg_parser = make_parser(program_name)
        try:
            options = arg_parser.parse_args(argv[1:])
            if len(options.files) <= 0:
                arg_parser.error("Please specify the files to trash.")
        except SystemExit as e:
            return ExitWithCode(type=ExitWithCode, exit_code=ensure_int(e.code))

        return Trash(type=Trash,
                     program_name=program_name,
                     options=options,
                     files=options.files,
                     trash_dir=options.trashdir,
                     mode=options.mode,
                     forced_volume=options.forced_volume,
                     verbose=options.verbose,
                     home_fallback=options.home_fallback)


def ensure_int(code):
    if not isinstance(code, int):
        raise ValueError("code must be an int, got %s" % pprint.pformat(code))
    return code


def make_parser(program_name):
    parser = ArgumentParser(prog=program_name,
                            usage="%(prog)s [OPTION]... FILE...",
                            description="Put files in trash",
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog="""\
To remove a file whose name starts with a '-', for example '-foo',
use one of these commands:

    trash -- -foo

    trash ./-foo

Report bugs to https://github.com/andreafrancia/trash-cli/issues""")
    add_argument_to(parser)
    parser.add_argument("-d", "--directory",
                        action="store_true",
                        help="ignored (for GNU rm compatibility)")
    parser.add_argument("-f", "--force",
                        action="store_const",
                        dest="mode",
                        const=mode_force,
                        help="silently ignore nonexistent files")
    parser.add_argument("-i", "--interactive",
                        action="store_const",
                        dest="mode",
                        const=mode_interactive,
                        help="prompt before every removal")
    parser.add_argument("-r", "-R", "--recursive",
                        action="store_true",
                        help="ignored (for GNU rm compatibility)")
    parser.add_argument("--trash-dir",
                        type=str,
                        action="store", dest='trashdir',
                        help='use TRASHDIR as trash folder'
                        ).complete = TRASH_DIRS
    parser.add_argument("-v",
                        "--verbose",
                        default=0,
                        action="count",
                        dest="verbose",
                        help="explain what is being done")
    parser.add_argument('--force-volume',
                        default=None,
                        action="store",
                        dest="forced_volume",
                        help=SUPPRESS)
    parser.add_argument('--home-fallback',
                        default=False,
                        action="store_true",
                        dest="home_fallback",
                        help=SUPPRESS)
    parser.add_argument("--version",
                        action="version",
                        version=version)
    parser.add_argument('files',
                        nargs='*'
                        ).complete = TRASH_FILES
    return parser
