from typing import Iterable, NamedTuple

from trashcli.empty.user import User


UserIntention = NamedTuple('UserIntention',
                           [('ok_to_empty', bool),
                            ('trash_dirs', Iterable[str])])


class Guard:

    def __init__(self, user):  # type: (User) -> None
        self.user = user

    def ask_the_user(self, parsed_interactive, trash_dirs
                     ):  # type: (bool, Iterable[str]) -> UserIntention
        if parsed_interactive:
            trash_dirs_list = list(trash_dirs)
            ok_to_empty = \
                self.user.do_you_wanna_empty_trash_dirs(trash_dirs_list)
            list_result = trash_dirs_list if ok_to_empty else []
            return UserIntention(ok_to_empty=ok_to_empty,
                                 trash_dirs=list_result)
        else:
            trash_dirs_list = trash_dirs
            return UserIntention(ok_to_empty=True,
                                 trash_dirs=trash_dirs_list)
