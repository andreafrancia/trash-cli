def a_trashinfo_without_deletion_date():
    return ("[Trash Info]\n"
            "Path=foo.txt\n")


def make_trashinfo(date):
    return ("[Trash Info]\n"
            "Path=foo.txt\n"
            "DeletionDate=%s" % date)


def an_empty_trashinfo():
    return ''
