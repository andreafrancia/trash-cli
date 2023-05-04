import unittest

from tests.test_put.support.fake_fs.fake_fs import FakeFs
from tests.test_restore.support.a_trashed_file import a_trashed_file
from tests.test_restore.support.has_been_restored_matcher import \
    has_been_restored


class TestHasBeenRestored(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.trashed_file = a_trashed_file(trashed_from='/original_location',
                                           info_file='/info_path.trashinfo',
                                           backup_copy='/backup_copy')

    def test_fail_if_original_location_does_not_exists(self):
        result = has_been_restored(self.fs).describe_mismatch(self.trashed_file,
                                                              focus_on='original_location')
        assert result == (
            "Expected file to be restore but it has not:\n"
            "  - FAIL original_location should exists but it does not: '/original_location'\n"
        )

    def test_ok_if_original_location_does_not_exists(self):
        self.fs.make_file('/original_location')
        result = has_been_restored(self.fs).describe_mismatch(self.trashed_file,
                                                              focus_on='original_location')
        assert result == (
            "Expected file to be restore but it has not:\n"
            "  - OK original_location should exists and it does: '/original_location'\n"
        )

    def test_fail_if_info_file_exists(self):
        self.fs.make_file('/info_path.trashinfo')
        result = has_been_restored(self.fs).describe_mismatch(self.trashed_file,
                                                              focus_on='info_file')
        assert result == (
            "Expected file to be restore but it has not:\n"
            "  - FAIL info_file should not exists but it does: '/info_path.trashinfo'\n"
        )

    def test_ok_if_info_file_does_not_exists(self):
        result = has_been_restored(self.fs).describe_mismatch(self.trashed_file,
                                                              focus_on='info_file')
        assert result == (
            "Expected file to be restore but it has not:\n"
            "  - OK info_file should not exists and it does not: '/info_path.trashinfo'\n"
        )

    def test_fail_if_backup_copy_exists(self):
        self.fs.make_file('/backup_copy')
        result = has_been_restored(self.fs).describe_mismatch(self.trashed_file,
                                                              focus_on='backup_copy')
        assert result == (
            "Expected file to be restore but it has not:\n"
            "  - FAIL backup_copy should not exists but it does: '/backup_copy'\n"
        )

    def test_ok_if_backup_copy_does_not_exists(self):
        result = has_been_restored(self.fs).describe_mismatch(self.trashed_file,
                                                              focus_on='backup_copy')
        assert result == (
            "Expected file to be restore but it has not:\n"
            "  - OK backup_copy should not exists and it does not: '/backup_copy'\n"
        )

    def test_fail_if_not_yet_restored(self):
        self.fs.make_file('/info_path.trashinfo')
        self.fs.make_file('/backup_copy')
        result = has_been_restored(self.fs).describe_mismatch(self.trashed_file)
        assert result == (
            "Expected file to be restore but it has not:\n"
            "  - FAIL original_location should exists but it does not: '/original_location'\n"
            "  - FAIL info_file should not exists but it does: '/info_path.trashinfo'\n"
            "  - FAIL backup_copy should not exists but it does: '/backup_copy'\n"
        )

    def test_ok_if_restored(self):
        self.fs.make_file('/original_location')
        result = has_been_restored(self.fs).describe_mismatch(self.trashed_file)
        assert result == (
            "Expected file to be restore but it has not:\n"
            "  - OK original_location should exists and it does: '/original_location'\n"
            "  - OK info_file should not exists and it does not: '/info_path.trashinfo'\n"
            "  - OK backup_copy should not exists and it does not: '/backup_copy'\n"
        )
