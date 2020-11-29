from integration_tests.files import (make_parent_for, write_file,
                                     make_unreadable_file)


class FakeTrashDir:
    def __init__(self, path):
        self.path = path + '/info'
        self.number = 1

    def add_unreadable_trashinfo(self, basename):
        path = self.a_trashinfo(basename)
        make_unreadable_file(path)

    def a_trashinfo(self, base_name):
        return'%(info_dir)s/%(name)s.trashinfo' % {'info_dir': self.path,
                                                    'name': base_name}

    def add_trashinfo(self, contents, base_name = None):
        if not base_name:
            base_name = str(self.number)
            self.number += 1
        path = '%(info_dir)s/%(name)s.trashinfo' % {'info_dir': self.path,
                                                    'name': base_name}
        make_parent_for(path)
        write_file(path, contents)

        self.path_of_last_file_added = path

    def add_trashinfo2(self, escaped_path_entry, formatted_deletion_date):
        self.add_trashinfo(a_trashinfo(escaped_path_entry, formatted_deletion_date))

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

def a_trashinfo_with_path(path):
    return ("[Trash Info]\n"
            "Path=%s\n" % path)
