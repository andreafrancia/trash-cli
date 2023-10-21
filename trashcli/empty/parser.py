import argparse

from typing import List

from trashcli.empty.empty_action import EmptyActionArgs
from trashcli.empty.print_time_action import PrintTimeArgs
from trashcli.lib.environ import Environ
from trashcli.lib.print_version import PrintVersionArgs
from trashcli.shell_completion import TRASH_DIRS, add_argument_to


class Parser:
    def parse(self,
              default_is_interactive,  # type: bool
              environ,  # type: Environ
              args,  # type: List[str]
              uid,  # type: int
              argv0,  # type: str
              ):
        parser = self.make_parser(default_is_interactive)
        namespace = parser.parse_args(args)

        if namespace.version:
            return PrintVersionArgs(
                argv0=argv0,
            )
        elif namespace.print_time:
            return PrintTimeArgs(environ=environ)
        else:
            return EmptyActionArgs(
                user_specified_trash_dirs=namespace.user_specified_trash_dirs,
                all_users=namespace.all_users,
                interactive=namespace.interactive,
                days=namespace.days,
                dry_run=namespace.dry_run,
                verbose=namespace.verbose,
                environ=environ,
                uid=uid,
            )

    @staticmethod
    def make_parser(default_is_interactive):
        parser = argparse.ArgumentParser(
            description='Purge trashed files.',
            epilog='Report bugs to https://github.com/andreafrancia/trash-cli/issues')
        add_argument_to(parser)
        parser.add_argument('--version', action='store_true', default=False,
                            help="show program's version number and exit")
        parser.add_argument("-v",
                            "--verbose",
                            default=0,
                            action="count",
                            dest="verbose",
                            help="list files that will be deleted",
                            )
        parser.add_argument('--trash-dir', action='append', default=[],
                            metavar='TRASH_DIR',
                            dest='user_specified_trash_dirs',
                            help='specify the trash directory to use'
                            ).complete = TRASH_DIRS
        parser.add_argument('--print-time', action='store_true',
                            dest='print_time',
                            help=argparse.SUPPRESS)
        parser.add_argument('--all-users', action='store_true',
                            dest='all_users',
                            help='empty all trashcan of all the users')
        parser.add_argument('-i',
                            '--interactive',
                            action='store_true',
                            dest='interactive',
                            help='ask before emptying trash directories',
                            default=default_is_interactive)
        parser.add_argument('-f',
                            action='store_false',
                            help='don\'t ask before emptying trash directories',
                            dest='interactive')
        parser.add_argument('--dry-run',
                            action='store_true',
                            help='show which files would have been removed',
                            dest='dry_run')
        parser.add_argument('days', action='store', default=None, type=int,
                            nargs='?')

        return parser
