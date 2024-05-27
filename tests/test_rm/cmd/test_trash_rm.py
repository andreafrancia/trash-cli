import unittest

from six import StringIO

from tests.support.py2mock import Mock

from tests.support.asserts import assert_starts_with
from trashcli.fstab.mount_points_listing import FakeMountPointsListing
from trashcli.rm.rm_cmd import RmCmd


class TestTrashRmCmdRun(unittest.TestCase):
    def setUp(self):
        self.stderr = StringIO()
        self.file_reader = Mock([])
        self.file_reader.exists = Mock([], return_value=None)
        self.file_reader.entries_if_dir_exists = Mock([], return_value=[])
        self.environ = {}
        self.mount_points_listing = FakeMountPointsListing([])
        self.getuid = lambda: '111'
        self.cmd = RmCmd(self.environ,
                         self.getuid,
                         self.stderr,
                         self.file_reader,
                         self.mount_points_listing)

    def test_without_arguments(self):
        self.cmd.run([None], uid=None)

        assert_starts_with(self.stderr.getvalue(),
                           'Usage:\n    trash-rm PATTERN\n\nPlease specify PATTERN.\n')

    def test_without_pattern_argument(self):
        self.mount_points_listing.set_mount_points(['/vol1'])

        self.cmd.run([None, None], uid=None)

        assert '' == self.stderr.getvalue()
