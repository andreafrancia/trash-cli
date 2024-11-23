from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.fs.fake_restore_fs import FakeRestoreFs


class TestStateFileHasBeenMoved:
    def setup_method(self):
        self.fs = FakeFs()
        self.restore_fs = FakeRestoreFs(self.fs)

    def test_file_moved_ok(self):
        self.restore_fs.add_file("/a/foo.txt", b"content")
        state = self.restore_fs.save_state()

        self.restore_fs.mkdirs("/b")
        self.restore_fs.move("/a/foo.txt", "/b/dest.txt")

        assert (state.check_file_moved("/a/foo.txt", "/b/dest.txt") ==
                '')

    def test_file_moved_didnt_existed(self):
        state = self.restore_fs.save_state()

        assert (state.check_file_moved("/a/foo.txt", "/b/dest.txt") ==
                'File not moved because source file did not exists: /a/foo.txt')

    def test_file_moved_but_changed(self):
        self.restore_fs.add_file("/a/foo.txt", b"content")
        state = self.restore_fs.save_state()

        self.restore_fs.mkdirs("/b")
        self.restore_fs.move("/a/foo.txt", "/b/dest.txt")
        self.restore_fs.write_file("/b/dest.txt", "different content")

        assert (state.check_file_moved("/a/foo.txt", "/b/dest.txt") ==
                'File not moved because destination contains a different content, '
                'dest: /b/dest.txt, '
                "dest content: 'different content'")

    def test_file_not_moved_because_dest_does_not_exists(self):
        self.restore_fs.add_file("/a/foo.txt", b"content")
        state = self.restore_fs.save_state()

        self.restore_fs.mkdirs("/b")
        self.restore_fs.move("/a/foo.txt", "/b/dest.txt")
        self.restore_fs.remove_file("/b/dest.txt")

        assert (state.check_file_moved("/a/foo.txt", "/b/dest.txt") ==
                'File not moved because destination does not exists: /b/dest.txt')

    def test_file_not_moved_because_dest_is_not_a_file(self):
        self.restore_fs.add_file("/a/foo.txt", b"content")
        state = self.restore_fs.save_state()

        self.restore_fs.mkdirs("/b")
        self.restore_fs.move("/a/foo.txt", "/b/dest.txt")
        self.restore_fs.remove_file("/b/dest.txt")
        self.restore_fs.mkdirs("/b/dest.txt")

        assert (state.check_file_moved("/a/foo.txt", "/b/dest.txt") ==
                'File not moved because destination is not a file: /b/dest.txt')
