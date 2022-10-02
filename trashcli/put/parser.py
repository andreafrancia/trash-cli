from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter

from trashcli.shell_completion import TRASH_DIRS, TRASH_FILES, add_argument_to
from trashcli.trash import version


mode_force = 'force'
mode_interactive = 'interactive'


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
    parser.add_argument("--version",
                        action="version",
                        version=version)
    parser.add_argument('files',
                        nargs='*'
                        ).complete = TRASH_FILES
    return parser
