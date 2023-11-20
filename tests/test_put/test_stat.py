from tests.run_command import temp_dir
from trashcli.put.fs.real_fs import RealFs


class TestStat:
    def test(self, temp_dir):
        fs = RealFs()
        fs.mkdir(temp_dir / 'foo')
        stat = fs.lstat(temp_dir / 'foo')
        assert stat.mode == 16877
