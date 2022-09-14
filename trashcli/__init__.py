import os

base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

TRASH_DIRS = {'zsh': '(${$(trash-list --trash-dirs)#parent_*:})'}
PREAMBLE = {
    "zsh": r"""
# https://github.com/zsh-users/zsh/blob/19390a1ba8dc983b0a1379058e90cd51ce156815/Completion/Unix/Command/_rm#L72-L74
_trash_files() {
  (( CURRENT > 0 )) && line[CURRENT]=()
  line=( ${line//(#m)[\[\]()\\*?#<>~\^\|]/\\$MATCH} )
  _files -F line
}
""",
}
