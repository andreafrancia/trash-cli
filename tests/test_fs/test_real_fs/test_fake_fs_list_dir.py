from tests.support.dirs.my_path import MyPath
from tests.support.put.fake_fs.fake_fs import FakeFs


class TestFakeFsListDir:
    def setup_method(self):
        self.fs = FakeFs()
        self.tmp_dir = MyPath('/tmp', self.fs)
        self.fs.makedirs(self.tmp_dir, 0o700)

    def test(self):
        self.fs.write_file(self.tmp_dir / 'a', 'content')
        self.fs.write_file(self.tmp_dir / 'b', 'content')
        self.fs.write_file(self.tmp_dir / 'c', 'content')
        self.fs.makedirs(self.tmp_dir / 'd', 0o700)

        assert sorted(self.fs.listdir(self.tmp_dir)) == ['a', 'b', 'c', 'd']
