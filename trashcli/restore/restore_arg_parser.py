import os
from typing import Union, List, cast

from trashcli.lib.print_version import PrintVersionArgs
from trashcli.restore.args import RunRestoreArgs, Sort
from trashcli.shell_completion import add_argument_to, TRASH_FILES, TRASH_DIRS, \
    complete_with

Command = Union[PrintVersionArgs, RunRestoreArgs]


class RestoreArgParser:
    def parse_restore_args(self,
                           sys_argv,  # type: List[str]
                           curdir,  # type: str
                           ):  # type: (...) -> Command
        import argparse

        parser = argparse.ArgumentParser(
            description='Restores from trash chosen file',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        add_argument_to(parser)
        complete_with(
            TRASH_FILES,
            parser.add_argument('path',
                                default="", nargs='?',
                                help='Restore files from given path instead of current '
                                     'directory'
                                )
        )
        parser.add_argument('--sort',
                            choices=['date', 'path', 'none'],
                            default='date',
                            help='Sort list of restore candidates by given field')
        complete_with(
            TRASH_DIRS,
            parser.add_argument('--trash-dir',
                                action='store',
                                dest='trash_dir',
                                help=argparse.SUPPRESS
                                ))
        parser.add_argument('--version', action='store_true', default=False)

        parser.add_argument('--overwrite',
                            action='store_true',
                            default=False,
                            help='Overwrite existing files with files coming out of the trash')

        parsed = parser.parse_args(sys_argv[1:])

        if parsed.version:
            return PrintVersionArgs(argv0=sys_argv[0])
        else:
            path = os.path.normpath(
                os.path.join(curdir + os.path.sep, parsed.path))

            return RunRestoreArgs(path=path,
                                  sort=cast(Sort, {
                                      'path': Sort.ByPath,
                                      'date': Sort.ByDate,
                                      'none': Sort.DoNot
                                  }[parsed.sort]),
                                  trash_dir=parsed.trash_dir,
                                  overwrite=parsed.overwrite)
