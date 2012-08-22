from nose.tools import raises

from integration_tests.files import require_empty_dir
from integration_tests.files import touch
from integration_tests.files import unset_sticky_bit
from integration_tests.files import set_sticky_bit

from mock import Mock

from trashcli.trash import mkdirs
from trashcli.trash import TopDirIsSymLink
from trashcli.trash import TopDirNotPresent
from trashcli.trash import TopDirWithoutStickyBit
from trashcli.trash import TopTrashDirRules

import os

class TestMethod1VolumeTrashDirectory:
    def setUp(self):
        require_empty_dir('sandbox')
        self.fs = Mock()
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = True
        self.checker = TopTrashDirRules(self.fs)
        self.out = Mock()

    def test_check_when_no_sticky_bit2(self):
        self.fs.has_sticky_bit.return_value = False

        self.valid_to_be_written2()

        self.out.not_valid_parent_should_be_sticky.assert_called_with()

    def test_check_when_no_dir2(self):
        self.fs.isdir.return_value = False

        self.valid_to_be_written2()

        self.out.not_valid_should_be_a_dir.assert_called_with()

    def test_check_when_is_symlink2(self):
        self.fs.islink.return_value = True

        self.valid_to_be_written2()

        self.out.not_valid_parent_should_not_be_a_symlink.assert_called_with()

    def test_check_pass2(self):

        self.valid_to_be_written2()

        self.out.is_valid()

    def valid_to_be_written2(self):
        self.checker.valid_to_be_written('sandbox/trash-dir/123', self.out)

    def test_check_pass(self):
        mkdirs('sandbox/trash-dir')
        set_sticky_bit('sandbox/trash-dir')

        self.valid_to_be_written()

    @raises(TopDirWithoutStickyBit)
    def test_check_when_no_sticky_bit(self):
        mkdirs("sandbox/trash-dir")
        unset_sticky_bit('sandbox/trash-dir')

        self.valid_to_be_written()

    @raises(TopDirNotPresent)
    def test_check_when_no_dir(self):
        touch('sandbox/trash-dir')
        set_sticky_bit('sandbox/trash-dir')

        self.valid_to_be_written()

    @raises(TopDirIsSymLink)
    def test_check_when_is_symlink(self):
        mkdirs('sandbox/trash-dir-dest')
        set_sticky_bit('sandbox/trash-dir-dest')
        os.symlink('trash-dir-dest', 'sandbox/trash-dir')

        self.valid_to_be_written()

    def valid_to_be_written(self):
        self.checker.check('sandbox/trash-dir/123')

