import os
from typing import NamedTuple, List, Union, Optional

from trashcli.lib.print_version import PrintVersionArgs
from trashcli.shell_completion import add_argument_to, TRASH_FILES, TRASH_DIRS



class RunRestoreArgs(
    NamedTuple('RunRestoreArgs', [
        ('path', str),
        ('sort', str),
        ('trash_dir', Optional[str]),
        ('overwrite', bool),
    ])):
    pass


Command = Union[PrintVersionArgs, RunRestoreArgs]


def parse_restore_args(sys_argv,  # type: List[str]
                       curdir,  # type: str
                       ):  # type: (...) -> Command
    import argparse

    parser = argparse.ArgumentParser(
        description='Restores from trash chosen file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_argument_to(parser)
    parser.add_argument('path',
                        default="", nargs='?',
                        help='Restore files from given path instead of current '
                             'directory'
                        ).complete = TRASH_FILES
    parser.add_argument('--sort',
                        choices=['date', 'path', 'none'],
                        default='date',
                        help='Sort list of restore candidates by given field')
    parser.add_argument('--trash-dir',
                        action='store',
                        dest='trash_dir',
                        help=argparse.SUPPRESS
                        ).complete = TRASH_DIRS
    parser.add_argument('--version', action='store_true', default=False)

    parser.add_argument('--overwrite',
                        action='store_true',
                        default=False,
                        help='Overwrite existing files with files coming out of the trash')

    parsed = parser.parse_args(sys_argv[1:])

    if parsed.version:
        return PrintVersionArgs(action="TODO",
                                argv0=sys_argv[0])
    else:
        path = os.path.normpath(os.path.join(curdir + os.path.sep, parsed.path))
        return RunRestoreArgs(path=path,
                              sort=parsed.sort,
                              trash_dir=parsed.trash_dir,
                              overwrite=parsed.overwrite)
