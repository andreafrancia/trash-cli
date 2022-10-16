import datetime
import os
import sys
import unittest

from tests.support.files import make_file
from tests.support.my_path import MyPath

from scripts import bump
from trashcli import base_dir
from trashcli.fs import read_file


sys.path.insert(0, os.path.join(base_dir, 'script'))


class Test_version_from_date(unittest.TestCase):
    def test(self):
        today = datetime.date(2021, 5, 11)
        result = bump.version_from_date(today)

        assert result == '0.21.5.11'


class Test_save_new_version(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        make_file(self.tmp_dir / 'trash.py', """\
somecode before
version="0.20.1.20"
somecode after
dont change this line: version="0.20.1.20"
""")

        bump.save_new_version('0.21.5.11', self.tmp_dir / 'trash.py')

        result = read_file(self.tmp_dir / "trash.py")
        assert result == """\
somecode before
version = '0.21.5.11'
somecode after
dont change this line: version="0.20.1.20"
"""

    def test2(self):
        make_file(self.tmp_dir / 'trash.py', """\
somecode before
    version="0.20.1.20"
somecode after
""")

        bump.save_new_version('0.21.5.11', self.tmp_dir / 'trash.py')

        result = read_file(self.tmp_dir / "trash.py")
        assert result == """\
somecode before
    version="0.20.1.20"
somecode after
"""

    def tearDown(self):
        self.tmp_dir.clean_up()
