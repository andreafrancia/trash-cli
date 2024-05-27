import datetime

from six.moves.urllib.parse import quote as url_quote

from trashcli.lib import TrashInfoContent


def format_trashinfo(original_location,  # type: str
                     deletion_date,  # type: datetime.datetime
                     ):  # type: (...) -> TrashInfoContent
    content = (b"[Trash Info]\n" +
               b"Path=%s\n" % format_original_location(original_location) +
               b"DeletionDate=%s\n" % format_date(deletion_date))
    return content


def format_date(deletion_date,  # type: datetime.datetime
                ):  # type: (...) -> TrashInfoContent
    return deletion_date.strftime("%Y-%m-%dT%H:%M:%S").encode('utf-8')


def format_original_location(original_location,  # type: str
                             ):  # type: (...) -> TrashInfoContent
    return url_quote(original_location, '/').encode('utf-8')
