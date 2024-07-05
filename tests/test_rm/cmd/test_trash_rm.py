import unittest

from six import StringIO

from tests.support.mock import Mock

from tests.support.asserts import assert_starts_with
from trashcli.rm.rm_cmd import RmCmd


class TestTrashRmCmdRun(unittest.TestCase):
    def setUp(self):
        self.volumes_listing = Mock()
        self.stderr = StringIO()
        self.file_reader = Mock([])
        self.file_reader.exists = Mock([], return_value=None)
        self.file_reader.entries_if_dir_exists = Mock([], return_value=[])
        self.environ = {}
        self.getuid = lambda: '111'
        self.cmd = RmCmd(self.environ,
                         self.getuid,
                         self.volumes_listing,
                         self.stderr,
                         self.file_reader)

    def test_without_arguments(self):
        self.cmd.run([None], uid=None)

        assert_starts_with(self.stderr.getvalue(),
                           'Usage:\n    trash-rm PATTERN\n\nPlease specify PATTERN.\n')

    def test_without_pattern_argument(self):
        self.volumes_listing.list_volumes.return_value = ['/vol1']

        self.cmd.run([None, None], uid=None)

        assert '' == self.stderr.getvalue()
