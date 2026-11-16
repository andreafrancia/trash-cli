from tests.support.put.fake_fs.fake_fs import FakeFs


class TestFakeFsRmdir:

    def test_rmdir(self):
        fs = FakeFs()
        fs.mkdir('/foo')
        fs.path_isdir('/foo')

        fs.rmdir('/foo')

        assert fs.path_isdir('/foo') == False
