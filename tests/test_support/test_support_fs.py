from tests.support.dirs.my_path import MyPath
from tests.support.dirs.support_fs import SupportFs
from tests.support.put.fake_fs.fake_fs import FakeFs


class TestSupportFs:
    def test_read__reads_a_file_relative_to_base_dir(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        base_dir.write_file('a', 'content of a')

        assert support_fs.read('a') == 'content of a'
