import datetime

import pytest

from tests.support.fakes.fake_file_system import FakeFileSystem
from tests.support.fakes.fake_file_system import UnreadableFileSystem
from trashcli.empty.clock import Clock
from trashcli.empty.delete_according_date import DeleteAccordingDate


class TestDeleteAccordingDateVanished:
    def setup_method(self):
        self.clock = Clock(lambda: datetime.datetime(2000, 1, 10), None)

    def test_trashinfo_removed_after_the_listing_is_skipped(self):
        delete_mode = DeleteAccordingDate(FakeFileSystem(), self.clock)

        result = delete_mode.ok_to_delete('/trash/info/a.trashinfo', {}, 2)

        assert result is False

    def test_other_read_errors_are_not_swallowed(self):
        delete_mode = DeleteAccordingDate(UnreadableFileSystem(), self.clock)

        with pytest.raises(IOError):
            delete_mode.ok_to_delete('/trash/info/a.trashinfo', {}, 2)
