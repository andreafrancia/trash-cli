from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.fs.fake_restore_fs import FakeRestoreFs


class TestStateCheckDirectoryIsCreated:
    def setup_method(self):
        self.fs = FakeFs()
        self.restore_fs = FakeRestoreFs(self.fs)

    def test_state_dir_already_existing(self):
        self.restore_fs.mkdirs("/pippo")
        state = self.restore_fs.save_state()

        assert (state.check_directory_created("/pippo") ==
                'already directory existed before: /pippo')

    def test_state_dir_created(self):
        state = self.restore_fs.save_state()
        self.restore_fs.mkdirs("/pippo")

        assert (state.check_directory_created("/pippo") ==
                '')

    def test_state_dir_not_created(self):
        state = self.restore_fs.save_state()

        assert (state.check_directory_created("/pippo") ==
                'directory has not been created: /pippo')

