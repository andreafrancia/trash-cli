def a_trashinfo(escaped_path_entry,
                formatted_deletion_date = '2000-01-01T00:00:01'):
    return ("[Trash Info]\n"                          +
            "Path=%s\n"         % escaped_path_entry +
            "DeletionDate=%s\n" % formatted_deletion_date)

def a_trashinfo_without_date():
    return ("[Trash Info]\n"
            "Path=/path\n")

def a_trashinfo_with_invalid_date():
    return ("[Trash Info]\n"
            "Path=/path\n"
            "DeletionDate=Wrong Date")

def a_trashinfo_without_path():
    return ("[Trash Info]\n"
            "DeletionDate='2000-01-01T00:00:00'\n")

def a_trashinfo_with_date(date):
    return ("[Trash Info]\n"
            "DeletionDate=%s\n" % date)
