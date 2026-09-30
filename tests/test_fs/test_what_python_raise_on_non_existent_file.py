import errno
import os
import tempfile

import pytest
import six


class TestWhatPythonRaiseOnNonExistentFile:
    @pytest.fixture(autouse=True)
    def test_reading_an_existing_file(self):
        assert os.path.exists(__file__) is True
        os.stat(__file__)  # do not raise any Exception

    def test_not_existing_file(self):
        temp_dir =  tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'not-existing-temp_file')
        assert os.path.exists(temp_file) is False

        with pytest.raises((OSError, IOError)) as e:
            os.stat(temp_file)
        os.rmdir(temp_dir)

        assert isinstance(e.value, OSError)
        assert e.value.strerror == 'No such file or directory'
        assert e.value.errno == errno.ENOENT
        assert e.value.filename == temp_file

        # python 2 and python 3 raises different exception
        if six.PY2:
            assert type(e.value) is OSError
        elif six.PY3:
            assert type(e.value) is FileNotFoundError
            # FileNotFoundError is a OSError and IOError subclass
            assert issubclass(FileNotFoundError, OSError)
            assert issubclass(FileNotFoundError, IOError)
        else:
            assert False

        # The FileNotFoundError exists only in python 3
        if six.PY2:
            import __builtin__
            assert hasattr(__builtin__, 'FileNotFoundError') is False
        elif six.PY3:
            import builtins
            assert hasattr(builtins, 'FileNotFoundError')
        else:
            assert False

        # In python2 IOError is different from OSError, in python3 they are
        # the same classe
        if six.PY2:
            assert (IOError is not OSError) and (OSError is not IOError)
        elif six.PY3:
            assert (IOError is OSError) and (IOError is OSError)
            # the real name of IOError is 'OSError'
            assert str(IOError) == "<class 'OSError'>"
        else:
            assert False
