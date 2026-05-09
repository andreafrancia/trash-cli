import os
import sys

import pytest
from six import binary_type

from tests.support.dirs.temp_dir import temp_dir
from tests.test_put.cmd.e2e.run_trash_put import run_trash_put2
from trashcli.lib.exit_codes import EX_OK

temp_dir = temp_dir

NON_UTF8_BASENAME = b'\xa4-\xc8\xcf-\xc1+\xb8.txt'
QUOTED_BASENAME = b'%A4-%C8%CF-%C1%2B%B8.txt'


@pytest.mark.slow
def test_trash_put_preserves_non_utf8_filename_bytes(temp_dir):
    env = {'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME',
           'HOME': temp_dir / 'home'}
    source_dir = _fsencode(temp_dir / 'source')
    if not os.path.isdir(source_dir):
        os.makedirs(source_dir)
    source_path = os.path.join(source_dir, NON_UTF8_BASENAME)
    _touch_bytes_path(source_path)

    result = run_trash_put2(temp_dir, [_fsdecode(source_path)], env)

    assert result.exit_code == EX_OK
    assert not os.path.exists(source_path)
    files_dir = _fsencode(temp_dir / 'XDG_DATA_HOME' / 'Trash' / 'files')
    assert os.listdir(files_dir) == [NON_UTF8_BASENAME]
    info_dir = _fsencode(temp_dir / 'XDG_DATA_HOME' / 'Trash' / 'info')
    info_entries = os.listdir(info_dir)
    assert info_entries == [NON_UTF8_BASENAME + b'.trashinfo']
    with open(os.path.join(info_dir, info_entries[0]), 'rb') as trashinfo:
        trashinfo_content = trashinfo.read()
    assert QUOTED_BASENAME in trashinfo_content


def _touch_bytes_path(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)


def _fsencode(path):
    if hasattr(os, 'fsencode'):
        return os.fsencode(path)
    if isinstance(path, binary_type):
        return path
    return path.encode(sys.getfilesystemencoding() or sys.getdefaultencoding())


def _fsdecode(path):
    if hasattr(os, 'fsdecode'):
        return os.fsdecode(path)
    return path
