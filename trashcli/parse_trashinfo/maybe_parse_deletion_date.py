# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import

from trashcli.parse_trashinfo.basket import Basket
from trashcli.parse_trashinfo.parse_trashinfo import ParseTrashInfo


def maybe_parse_deletion_date(contents):
    result = Basket(unknown_date)
    parser = ParseTrashInfo(
        on_deletion_date=lambda date: result.collect(date),
        on_invalid_date=lambda: result.collect(unknown_date)
    )
    parser.parse_trashinfo(contents)
    return result.collected


unknown_date = '????-??-?? ??:??:??'
