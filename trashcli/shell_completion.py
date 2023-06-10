import argparse
from copy import copy

from typing import Dict

try:
    def convert_to_list(tuple):
        return [item for item in tuple]


    from shtab import add_argument_to, FILE, DIR  # type: ignore

    defaults = convert_to_list(add_argument_to.__defaults__)
    defaults[-1] = {
        "zsh": r"""
# https://github.com/zsh-users/zsh/blob/19390a1ba8dc983b0a1379058e90cd51ce156815/Completion/Unix/Command/_rm#L72-L74
_trash_files() {
  (( CURRENT > 0 )) && line[CURRENT]=()
  line=( ${line//(#m)[\[\]()\\*?#<>~\^\|]/\\$MATCH} )
  _files -F line
}
""",
    }
    add_argument_to.__defaults__ = tuple(defaults)
    TRASH_FILES = copy(FILE)
    TRASH_DIRS = copy(DIR)


    def complete_with(completion,  # type: Dict[str, str]
                      action,  # type: argparse.Action
                      ):
        action.complete = completion  # type: ignore



except ImportError:
    from argparse import Action

    TRASH_FILES = TRASH_DIRS = {}


    class PrintCompletionAction(Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print('Please install shtab firstly!')
            parser.exit(0)


    def add_argument_to(parser, *args, **kwargs):  # type: ignore
        Action.complete = None  # type: ignore
        parser.add_argument(
            '--print-completion',
            choices=['bash', 'zsh', 'tcsh'],
            action=PrintCompletionAction,
            help='print shell completion script',
        )
        return parser


    def complete_with(completion,  # type: Dict[str, str]
                      action,  # type: argparse.Action
                      ):
        pass

TRASH_FILES.update({"zsh": "_trash_files"})
TRASH_DIRS.update({"zsh": "(${$(trash-list --trash-dirs)#parent_*:})"})
