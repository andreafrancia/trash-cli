import datetime
import unittest

from flexmock import Mock
from six import StringIO

from tests.put.support.dummy_clock import DummyClock
from tests.put.support.fake_fs.fake_fs import FakeFs
from trashcli.fstab import create_fake_volume_of
from trashcli.put.access import Access
from trashcli.put.main import make_cmd
from trashcli.trash import EX_IOERR


class TestPut(unittest.TestCase):
    def setUp(self):
        access = Mock(spec=Access)
        clock = DummyClock(now_value=datetime.datetime(2014, 1, 1, 0, 0, 0))
        fs = FakeFs()
        my_input = lambda: "y"
        randint = lambda: 44
        volumes = create_fake_volume_of(['/'])
        self.stderr = StringIO()
        self.cmd = make_cmd(access=access, clock=clock, fs=fs,
                            my_input=my_input,
                            randint=randint, stderr=self.stderr,
                            volumes=volumes)

    def test_put(self):
        result = self.run_cmd(['trash-put', '-vvv', 'file'], {}, 123)

        assert result == [
            ['trash-put: volume of file: /',
             'trash-put: found unusable .Trash dir (should be a dir): /.Trash',
             'trash-put: trash directory /.Trash/123 is not secure',
             'trash-put: trying trash dir: /.Trash-123 from volume: /',
             'trash-put: .trashinfo created as /.Trash-123/info/file.trashinfo.',
             'trash-put: failed to trash file in /.Trash-123, because: no such file or directory: file',
             "trash-put: cannot trash non existent 'file'"],
            'None',
            EX_IOERR
        ]

    def test_put_home(self):
        result = self.run_cmd(['trash-put', '-vvv', 'file'],
                              {"HOME": "/home/user"}, 123)

        assert result == [
            ['trash-put: volume of file: /',
             'trash-put: trying trash dir: /home/user/.local/share/Trash from volume: /',
             'trash-put: .trashinfo created as '
             '/home/user/.local/share/Trash/info/file.trashinfo.',
             'trash-put: failed to trash file in ~/.local/share/Trash, because: no such '
             'file or directory: file',
             'trash-put: found unusable .Trash dir (should be a dir): /.Trash',
             'trash-put: trash directory /.Trash/123 is not secure',
             'trash-put: trying trash dir: /.Trash-123 from volume: /',
             'trash-put: .trashinfo created as /.Trash-123/info/file.trashinfo.',
             'trash-put: failed to trash file in /.Trash-123, because: no such file or '
             'directory: file',
             "trash-put: cannot trash non existent 'file'"],
            'None',
            EX_IOERR
        ]

    def test_when_file_does_not_exist(self):
        result = self.run_cmd(['trash-put', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result == [
            ["trash-put: cannot trash non existent 'non-existent'"],
            'None',
            EX_IOERR
        ]

    def run_cmd(self, args, environ, uid):
        err = None
        exit_code = None
        try:
            exit_code = self.cmd.run(args, environ, uid)
        except IOError as e:
            err = e
        stderr = self.stderr.getvalue().splitlines()

        return [stderr, str(err), exit_code]
