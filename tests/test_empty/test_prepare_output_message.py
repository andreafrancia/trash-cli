import unittest

from trashcli.empty.prepare_output_message import prepare_output_message
from trashcli.trash_dirs_scanner import trash_dir_found


class TestPrepareOutputMessage(unittest.TestCase):
    def test_one_dir(self):
        trash_dirs = [
            (trash_dir_found, ('/Trash', '/')),
        ]
        result = prepare_output_message(trash_dirs)

        assert """\
Would empty the following trash directories:
    - /Trash
Proceed? (y/N) """ == result

    def test_multiple_dirs(self):
        trash_dirs = [
            (trash_dir_found, ('/Trash1', '/')),
            (trash_dir_found, ('/Trash2', '/')),
        ]
        result = prepare_output_message(trash_dirs)

        assert """\
Would empty the following trash directories:
    - /Trash1
    - /Trash2
Proceed? (y/N) """ == result

    def test_no_dirs(self):
        trash_dirs = []

        result = prepare_output_message(trash_dirs)

        assert """\
No trash directories to empty.
""" == result
