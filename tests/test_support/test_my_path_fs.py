from tests.support.dirs.my_path import MyPath
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.real.real_fs import RealFs


class TestMyPathFs:
    def test_the_fs_can_be_set_from_outside(self):
        fs = FakeFs()

        assert MyPath('/x', fs).fs is fs

    def test_the_fs_can_be_set_by_keyword(self):
        fs = FakeFs()

        assert MyPath('/x', fs=fs).fs is fs

    def test_by_default_the_fs_is_real(self):
        assert isinstance(MyPath('/x').fs, RealFs)

    def test_it_is_still_the_str(self):
        assert MyPath('/x', FakeFs()) == '/x'

    def test_it_works_with_the_fake_fs(self):
        fs = FakeFs()
        path = MyPath('/x', fs)

        path.mkdirs()

        assert fs.path_isdir('/x') is True
        assert path.is_dir() is True

    def test_path_join_keeps_the_fs(self):
        fs = FakeFs()

        assert (MyPath('/x', fs) / 'a').fs is fs

    def test_path_join_keeps_the_fs_with_div(self):
        fs = FakeFs()

        assert MyPath('/x', fs).path_join('a').fs is fs

    def test_parent_keeps_the_fs(self):
        fs = FakeFs()

        assert MyPath('/x/y', fs).parent.fs is fs

    def test_find_all_keeps_the_fs(self):
        fs = FakeFs()
        path = MyPath('/x', fs)
        path.mkdirs()
        path.write_file('a', 'content')

        found = list(path.find_all())

        assert found == ['/x/a']
        assert [p.fs for p in found] == [fs]
