import datetime

from trashcli.trashinfo_path import quote_trashinfo_path


def format_trashinfo(original_location,  # type: str
                     deletion_date,  # type: datetime.datetime
                     ):
    content = ("[Trash Info]\n" +
               "Path=%s\n" % format_original_location(original_location) +
               "DeletionDate=%s\n" % format_date(deletion_date)).encode('utf-8')
    return content


def format_date(deletion_date):  # type: (datetime.datetime) -> str
    return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")


def format_original_location(original_location):  # type: (str) -> str
    return quote_trashinfo_path(original_location)
