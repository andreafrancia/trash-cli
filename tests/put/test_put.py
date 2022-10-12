import datetime
import unittest

from flexmock import Mock
from six import StringIO

from tests.put.support.dummy_clock import DummyClock
from tests.put.support.fake_fs.fake_fs import FakeFs
from trashcli.fstab import create_fake_volume_of
from trashcli.put.access import Access
from trashcli.put.main import do_main
from trashcli.trash import EX_IOERR


class TestPut(unittest.TestCase):
    def test_put(self):
        access = Mock(spec=Access)
        clock = DummyClock(now_value=datetime.datetime(2014, 1, 1, 0, 0, 0))
        fs = FakeFs()
        my_input = lambda: "y"
        randint = lambda: 44
        volumes = create_fake_volume_of(['/'])
        stderr = StringIO()
        err = None
        exit_code = None
        try:
            exit_code = do_main(access=access,
                                argv=['trash-put', '-vvv', 'file'],
                                clock=clock,
                                environ={},
                                fs=fs,
                                my_input=my_input,
                                randint=randint,
                                stderr=stderr,
                                uid=123,
                                volumes=volumes)
        except IOError as e:
            err = e
        assert [
                   stderr.getvalue().splitlines(),
                   str(err),
                   exit_code,
               ] == [
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
