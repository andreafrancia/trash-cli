try:
    from shtab import add_argument_to

    defaults = list(add_argument_to.__defaults__)
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
except ImportError:
    from argparse import Action

    class PrintCompletionAction(Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print('Please install shtab firstly!')
            parser.exit(0)

    def add_argument_to(parser, *args, **kwargs):

        Action.complete = None  # type: ignore
        parser.add_argument(
            '--print-completion',
            choices=['bash', 'zsh', 'tcsh'],
            action=PrintCompletionAction,
            help='print shell completion script',
        )
        return parser


TRASH_FILES = {"zsh": "_trash_files"}
TRASH_DIRS = {"zsh": "(${$(trash-list --trash-dirs)#parent_*:})"}
