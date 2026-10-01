from __future__ import absolute_import

import pwd
from typing import Iterable

from trashcli.lib.protocols.get_all_users import GetPwAll
from trashcli.lib.protocols.pwd_user import PwdUser


class RealGetPwAll(GetPwAll):
    def get_pw_all(self): # type: ()-> Iterable[PwdUser]
        for p in pwd.getpwall():
            yield PwdUser(p.pw_dir, p.pw_uid)
