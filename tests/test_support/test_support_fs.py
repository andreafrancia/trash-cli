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

    def test_existence_of_single__reports_relative_to_base_dir(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        base_dir.write_file('a', 'content of a')

        assert support_fs.existence_of_single('a') == '/a: exists'
        assert support_fs.existence_of_single('b') == '/b: does not exist'

    def test_existence_of__uses_the_fs(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        base_dir.write_file('a', '')

        assert support_fs.existence_of('a', 'b') == ['/a: exists',
                                                      '/b: does not exist']

    def test_exists__uses_the_fs(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        base_dir.write_file('a', '')

        assert support_fs.exists('a') is True
        assert support_fs.exists('/a') is True
        assert support_fs.exists('b') is False

    def test_find_all__keeps_the_fs(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        base_dir.write_file('a', 'content')

        found = list(support_fs.find_all())

        assert found == ['/x/a']
        assert [p.fs for p in found] == [fs]
