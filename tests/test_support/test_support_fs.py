from tests.support.dirs.my_path import MyPath
from tests.support.dirs.support_fs import SupportFs
from tests.support.put.fake_fs.fake_fs import FakeFs


class TestSupportFs:
    def test_read__reads_a_file_relative_to_base_dir(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        support_fs.write_file('a', 'content of a')

        assert support_fs.read('a') == 'content of a'

    def test_existence_of_single__reports_relative_to_base_dir(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        support_fs.write_file('a', 'content of a')

        assert support_fs.existence_of_single('a') == '/a: exists'
        assert support_fs.existence_of_single('b') == '/b: does not exist'

    def test_existence_of__uses_the_fs(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        support_fs.write_file('a', '')

        assert support_fs.existence_of('a', 'b') == ['/a: exists',
                                                      '/b: does not exist']

    def test_exists__uses_the_fs(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        support_fs.write_file('a', '')

        assert support_fs.exists('a') is True
        assert support_fs.exists('/a') is True
        assert support_fs.exists('b') is False

    def test_find_all__keeps_the_fs(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        support_fs.write_file('a', 'content')

        found = list(support_fs.find_all())

        assert found == ['/x/a']
        assert [p.fs for p in found] == [fs]

    def test_is_file__uses_the_fs(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        support_fs.write_file('a', '')

        assert support_fs.is_file('a') is True
        assert support_fs.is_file(base_dir / 'a') is True
        assert support_fs.is_file('b') is False

    def test_find_files_rel__lists_only_files_relative_to_base_dir(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        base_dir.mkdir_rel('dir')
        support_fs.write_file('a', '')
        support_fs.write_file('dir/b', '')

        assert sorted(support_fs.find_files_rel()) == ['/a', '/dir/b']

    def test_is_dir__uses_the_fs(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        base_dir.mkdir_rel('dir')

        assert support_fs.is_dir('dir') is True
        assert support_fs.is_dir(base_dir / 'dir') is True
        assert support_fs.is_dir('missing') is False

    def test_touch__creates_the_file_relative_to_base_dir(self):
        fs = FakeFs()
        base_dir = MyPath('/x', fs)
        support_fs = SupportFs(fs, base_dir)

        base_dir.mkdirs()
        support_fs.touch('a')

        assert support_fs.is_file('a') is True
