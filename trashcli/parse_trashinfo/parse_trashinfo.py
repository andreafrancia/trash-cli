from __future__ import absolute_import

import datetime
from six.moves.urllib.parse import unquote


def do_nothing(*argv, **argvk): pass


class ParseTrashInfo:
    def __init__(self,
                 on_deletion_date=do_nothing,
                 on_invalid_date=do_nothing,
                 on_path=do_nothing):
        self.found_deletion_date = on_deletion_date
        self.found_invalid_date = on_invalid_date
        self.found_path = on_path

    def parse_trashinfo(self, contents):
        found_deletion_date = False
        for line in contents.split('\n'):
            if not found_deletion_date and line.startswith('DeletionDate='):
                found_deletion_date = True
                try:
                    date = datetime.datetime.strptime(
                        line, "DeletionDate=%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    self.found_invalid_date()
                else:
                    self.found_deletion_date(date)

            if line.startswith('Path='):
                path = unquote(line[len('Path='):])
                self.found_path(path)
