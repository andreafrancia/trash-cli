from trashcli.py2compat import url_quote


def format_trashinfo(original_location, deletion_date):
    content = ("[Trash Info]\n" +
               "Path=%s\n" % format_original_location(original_location) +
               "DeletionDate=%s\n" % format_date(deletion_date)).encode('utf-8')
    return content


def format_date(deletion_date):
    return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")


def format_original_location(original_location):
    return url_quote(original_location, '/')
