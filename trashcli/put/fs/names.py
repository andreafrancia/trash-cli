import grp
import pwd
from typing import Optional


class Names:
    def username(self, uid):  # type: (int) -> Optional[str]
        try:
            return pwd.getpwuid(uid).pw_name
        except KeyError as e:
            return None

    def groupname(self, gid):
        try:
            return grp.getgrgid(gid).gr_name
        except KeyError as e:
            return None
