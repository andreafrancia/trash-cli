from __future__ import absolute_import

from trashcli.lib import TrashInfoContent
from trashcli.parse_trashinfo.parse_trashinfo import ParseTrashInfo
from trashcli.parse_trashinfo.basket import Basket
import datetime

def parse_deletion_date(contents,  # type: TrashInfoContent
                        ):  # type: (...) -> datetime.datetime
    result = Basket()
    parser = ParseTrashInfo(on_deletion_date=result.collect)
    parser.parse_trashinfo(contents)
    return result.collected
