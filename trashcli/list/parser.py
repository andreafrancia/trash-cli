import argparse

from trashcli.list.actions import Action
from trashcli.shell_completion import add_argument_to, TRASH_DIRS


class Parser:
    def __init__(self, prog):
        self.parser = argparse.ArgumentParser(prog=prog,
                                              description='List trashed files',
                                              epilog='Report bugs to https://github.com/andreafrancia/trash-cli/issues')
        add_argument_to(self.parser)
        self.parser.add_argument('--version',
                                 dest='action',
                                 action='store_const',
                                 const=Action.print_version,
                                 default=Action.list_trash,
                                 help="show program's version number and exit")
        self.parser.add_argument('--debug-volumes',
                                 dest='action',
                                 action='store_const',
                                 const=Action.debug_volumes,
                                 help=argparse.SUPPRESS)
        self.parser.add_argument('--volumes',
                                 dest='action',
                                 action='store_const',
                                 const=Action.list_volumes,
                                 help="list volumes")
        self.parser.add_argument('--trash-dirs',
                                 dest='action',
                                 action='store_const',
                                 const=Action.list_trash_dirs,
                                 help="list trash dirs")
        self.parser.add_argument('--trash-dir',
                                 action='append',
                                 default=[],
                                 dest='trash_dirs',
                                 help='specify the trash directory to use'
                                 ).complete = TRASH_DIRS
        self.parser.add_argument('--size',
                                 action='store_const',
                                 default='deletion_date',
                                 const='size',
                                 dest='attribute_to_print',
                                 help=argparse.SUPPRESS)
        self.parser.add_argument('--files',
                                 action='store_true',
                                 default=False,
                                 dest='show_files',
                                 help=argparse.SUPPRESS)
        self.parser.add_argument('--all-users',
                                 action='store_true',
                                 dest='all_users',
                                 help='list trashcans of all the users')
        self.parser.add_argument('--python',
                                 dest='action',
                                 action='store_const',
                                 const=Action.print_python_executable,
                                 help=argparse.SUPPRESS)

    def parse_list_args(self, args):
        parsed = self.parser.parse_args(args)
        return parsed
