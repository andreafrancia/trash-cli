from tests.support.put.fake_fs.fake_fs import FakeFs


class TestRealpath:
    def setup_method(self):
        self.fs = FakeFs()

    def test(self):
        self.fs.touch("pippo")

        assert self.fs.realpath("pippo") == "/pippo"

    def test_cur_dir_with_several_paths(self):
        self.fs.mkdir("music")
        self.fs.cd("music")
        self.fs.make_file_and_dirs("be/bop/a/lula")

        assert self.fs.realpath("be/bop/a/lula") == "/music/be/bop/a/lula"





