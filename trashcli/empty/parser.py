import argparse

from trashcli.empty.actions import Action


class Parser:
    def parse(self, default_is_interactive, args):
        parser = self.make_parser(default_is_interactive)
        return parser.parse_args(args)

    @staticmethod
    def make_parser(default_is_interactive):
        parser = argparse.ArgumentParser(
            description='Purge trashed files.',
            epilog='Report bugs to https://github.com/andreafrancia/trash-cli/issues')
        parser.set_defaults(action=Action.empty)
        parser.add_argument('--version', action='store_true', default=False,
                            help="show program's version number and exit")
        parser.add_argument('--trash-dir', action='append', default=[],
                            metavar='TRASH_DIR',
                            dest='user_specified_trash_dirs',
                            help='specify the trash directory to use')
        parser.add_argument('--print-time', action='store_true', dest='print_time',
                            help=argparse.SUPPRESS)
        parser.add_argument('--all-users', action='store_true', dest='all_users',
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
        parser.add_argument('days', action='store', default=None, type=int,
                            nargs='?')

        return parser
