from tests.support.dirs.my_path import MyPath
from tests.support.dirs.support_fs import SupportFs
from tests.support.put.fake_fs.fake_fs import FakeFs


class TestMyPathFs:
    def test_my_path__need_fs(self):
        fs = FakeFs()

        assert MyPath('/x', fs).fs is fs

    def test_the_fs_can_be_set_by_keyword(self):
        fs = FakeFs()

        assert MyPath('/x', fs=fs).fs is fs


    def test_mypath__is_a_str(self):
        assert MyPath('/x', FakeFs()) == '/x'

    def test_path_join__keeps_the_fs(self):
        fs = FakeFs()

        assert (MyPath('/x', fs) / 'a').fs is fs

    def test_path_join_with_div___keeps_the_fs_with_div(self):
        fs = FakeFs()

        assert MyPath('/x', fs).path_join('a').fs is fs

    def test_parent__keeps_the_fs(self):
        fs = FakeFs()

        assert MyPath('/x/y', fs).parent.fs is fs

    def test_clean_up__uses_the_fs(self):
        fs = FakeFs()
        path = MyPath('/x', fs)
        support_fs = SupportFs(fs, path)

        support_fs.mkdirs()
        support_fs.write_file('a', '')

        path.clean_up()

        assert fs.path_exists('/x') is False
