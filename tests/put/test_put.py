import unittest

from flexmock import flexmock, Mock
from six import StringIO

from tests.put.support.dummy_clock import DummyClock
from tests.put.support.fake_fs.fake_fs import FakeFs
from trashcli.fstab import Volumes, create_fake_volume_of
from trashcli.put.access import Access
from trashcli.put.main import do_main


class TestPut(unittest.TestCase):
    def test_put(self):
        access = Mock(spec=Access)
        clock = DummyClock()
        fs = FakeFs()
        my_input = lambda: "y"
        randint = lambda: 44
        realpath = lambda path: path
        volumes = create_fake_volume_of(['/'])
        stderr = StringIO()
        err = None
        try:
            result = do_main(access=access,
                             argv=['trash-put', '-vvv', 'file'],
                             clock=clock,
                             environ={},
                             fs=fs,
                             my_input=my_input,
                             randint=randint,
                             realpath=realpath,
                             stderr=stderr,
                             uid=123,
                             volumes=volumes)
        except IOError as e:
            err = e
        assert stderr.getvalue().splitlines() == ['trash-put: volume of file: ']
        assert str(err) == 'no such file or directory: .Trash'
