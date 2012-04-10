# Copyright (C) 2008-2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import has_sticky_bit, mkdirs, FileSystemReader

from .files import require_empty_dir, having_file, set_sticky_bit
import os

class TestWithInSandbox:
    def test_mkdirs_with_default_mode(self):

        mkdirs("sandbox/test-dir/sub-dir")

        assert os.path.isdir("sandbox/test-dir/sub-dir")

    def test_has_sticky_bit_returns_true(self):

        having_file( "sandbox/sticky")
        run('chmod +t sandbox/sticky')

        assert has_sticky_bit('sandbox/sticky')
        
    def test_has_sticky_bit_returns_false(self):

        having_file( "sandbox/non-sticky")
        run('chmod -t sandbox/non-sticky')

        assert not has_sticky_bit("sandbox/non-sticky")

    def setUp(self):
        require_empty_dir('sandbox')

is_sticky_dir=FileSystemReader().is_sticky_dir
class Test_is_sticky_dir:

    def test_dir_non_sticky(self):
        mkdirs('sandbox/dir'); assert not is_sticky_dir('sandbox/dir')

    def test_dir_sticky(self):
        mkdirs('sandbox/dir'); set_sticky_bit('sandbox/dir')
        assert is_sticky_dir('sandbox/dir')

    def test_non_dir_but_sticky(self):
        having_file('sandbox/dir');
        set_sticky_bit('sandbox/dir')
        assert not is_sticky_dir('sandbox/dir')

    def setUp(self):
        require_empty_dir('sandbox')

def run(command):
    import subprocess
    assert subprocess.call(command.split()) == 0

