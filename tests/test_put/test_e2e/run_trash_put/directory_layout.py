from tests.test_put.test_e2e.run_trash_put import PutResult
from tests.test_put.test_e2e.run_trash_put import run_trash_put4


class Result:
    def __init__(self,
                 layout,  # type: DirectoriesLayout
                 output,  # type: PutResult
                 ):
        self.output = output
        self.layout = layout

    def status(self):
        return {
            'command output': "\n".join(self.output.stderr.lines()),
            'file left in current_dir': self.layout.cur_dir.list_all_files_sorted(),
            'file in trash dir': self.layout.trash_dir.list_all_files_sorted(),
        }


class DirectoriesLayout:
    def __init__(self, root_dir, fs):
        self.root_dir = root_dir
        self.fs = fs

    @property
    def cur_dir(self):
        return self.root_dir / 'cur-dir'

    @property
    def trash_dir(self):
        return self.root_dir / 'trash-dir'

    def make_cur_dir(self):
        self.fs.mkdir(self.cur_dir)

    def run_trash_put(self,
                      args,  # type: list[str]
                      ):  # type: (...) -> Result
        output = run_trash_put4(self.root_dir, self.cur_dir, self.trash_dir,
                                args,
                                env={})
        return Result(self, output)

    def mkdir_in_cur_dir(self, relative_path):
        self.fs.mkdir(self.cur_dir / relative_path)

    def touch_in_cur_dir(self, relative_path):
        self.fs.touch(self.cur_dir / "a-file")

    def symlink_in_cur_dir(self, src, dest):
        self.fs.symlink(self.cur_dir / src, self.cur_dir / dest)
