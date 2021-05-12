from trashcli.fs import read_file, write_file
import re


def version_from_date(today):
    return "0.%s.%s.%s" % (today.year % 100,
                           today.month,
                           today.day)


def save_new_version(new_version, path):
    content = read_file(path)
    new_content = re.sub('version=.*', 'version = \'%s\'' % new_version,
                         content)
    write_file(path, new_content)

