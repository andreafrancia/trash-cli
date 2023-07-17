import argparse
from typing import List, Union

from trashcli.lib.print_version import PrintVersionArgs
from trashcli.list.list_trash_action import ListTrashArgs
from trashcli.list.minor_actions.debug_volumes import DebugVolumesArgs
from trashcli.list.minor_actions.list_trash_dirs import ListTrashDirsArgs
from trashcli.list.minor_actions.list_volumes import PrintVolumesArgs
from trashcli.list.minor_actions.print_python_executable import \
    PrintPythonExecutableArgs
from trashcli.shell_completion import add_argument_to, TRASH_DIRS
from trashcli.super_enum import SuperEnum

Args = Union[
    PrintVersionArgs,
    PrintVolumesArgs,
    DebugVolumesArgs,
    ListTrashDirsArgs,
    ListTrashArgs,
    PrintPythonExecutableArgs
]


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
        self.parser.add_argument('--currentdir',
                                 action='store_true',
                                 default=False,
                                 dest='only_print_wd',
                                 help="Only show files trashed from current directory")
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

    def parse_list_args(self,
                        args,  # type: List[str]
                        argv0,  # type: str
                        ):  # type: (...) -> Args

        parsed = self.parser.parse_args(args)

        if parsed.action == Action.print_version:
            return PrintVersionArgs(argv0=argv0)
        if parsed.action == Action.list_volumes:
            return PrintVolumesArgs()
        if parsed.action == Action.debug_volumes:
            return DebugVolumesArgs()
        if parsed.action == Action.list_trash_dirs:
            return ListTrashDirsArgs(
                trash_dirs=parsed.trash_dirs,
                all_users=parsed.all_users
            )
        if parsed.action == Action.list_trash:
            return ListTrashArgs(
                trash_dirs=parsed.trash_dirs,
                attribute_to_print=parsed.attribute_to_print,
                show_files=parsed.show_files,
                only_print_wd=parsed.only_print_wd,
                all_users=parsed.all_users
            )
        if parsed.action == Action.print_python_executable:
            return PrintPythonExecutableArgs()

        raise ValueError('Unknown action: {}'.format(parsed.action))


class Action(SuperEnum):
    debug_volumes = 'debug_volumes'
    print_version = 'print_version'
    list_trash = 'list_trash'
    list_volumes = 'list_volumes'
    list_trash_dirs = 'list_trash_dirs'
    print_python_executable = 'print_python_executable'
