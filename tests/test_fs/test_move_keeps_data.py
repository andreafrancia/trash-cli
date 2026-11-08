import errno
import os
import shutil
import tempfile

import pytest

from trashcli.fslib.real import real_move
from trashcli.fslib.real.real_move import RealMove


@pytest.mark.skipif(os.geteuid() == 0, reason="root can move and delete anyway")
class TestMoveKeepsData:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, 'src', 'dir', 'sub'))
        open(os.path.join(self.tmp, 'src', 'dir', 'sub', 'file'), 'w').close()
        os.mkdir(os.path.join(self.tmp, 'dest'))
        os.chmod(os.path.join(self.tmp, 'src', 'dir'), 0o555)

    def teardown_method(self):
        for root, dirs, _ in os.walk(self.tmp):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
        shutil.rmtree(self.tmp)

    def test_a_dir_that_cannot_be_renamed_stays_complete(self):
        with pytest.raises(OSError):
            RealMove().move(os.path.join(self.tmp, 'src', 'dir'), os.path.join(self.tmp, 'dest', 'dir'))

        assert os.path.exists(os.path.join(self.tmp, 'src', 'dir', 'sub', 'file'))
        assert not os.path.exists(os.path.join(self.tmp, 'dest', 'dir'))

    def test_a_dir_is_moved_across_file_systems(self, monkeypatch):
        monkeypatch.setattr(real_move.os, 'rename', rename_across_file_systems)
        os.chmod(os.path.join(self.tmp, 'src', 'dir'), 0o755)

        RealMove().move(os.path.join(self.tmp, 'src', 'dir'), os.path.join(self.tmp, 'dest', 'dir'))

        assert os.listdir(os.path.join(self.tmp, 'src')) == []
        assert os.path.exists(os.path.join(self.tmp, 'dest', 'dir', 'sub', 'file'))

    def test_a_dir_that_cannot_be_removed_is_left_unchanged(self, monkeypatch):
        monkeypatch.setattr(real_move.os, 'rename', rename_across_file_systems)

        with pytest.raises(OSError):
            RealMove().move(os.path.join(self.tmp, 'src', 'dir'), os.path.join(self.tmp, 'dest', 'dir'))

        assert os.path.exists(os.path.join(self.tmp, 'src', 'dir', 'sub', 'file'))
        assert os.listdir(os.path.join(self.tmp, 'src')) == ['dir']
        assert os.listdir(os.path.join(self.tmp, 'dest')) == []

    def test_a_failed_copy_leaves_nothing(self, monkeypatch):
        monkeypatch.setattr(real_move.os, 'rename', rename_across_file_systems)
        os.chmod(os.path.join(self.tmp, 'src', 'dir', 'sub'), 0o300)

        with pytest.raises(EnvironmentError):
            RealMove().move(os.path.join(self.tmp, 'src', 'dir'), os.path.join(self.tmp, 'dest', 'dir'))

        assert os.listdir(os.path.join(self.tmp, 'dest')) == []

    def test_an_existing_destination_is_not_removed(self, monkeypatch):
        monkeypatch.setattr(real_move.os, 'rename', rename_across_file_systems)
        os.mkdir(os.path.join(self.tmp, 'dest', 'dir'))
        open(os.path.join(self.tmp, 'dest', 'dir', 'keep'), 'w').close()

        with pytest.raises(OSError):
            RealMove().move(os.path.join(self.tmp, 'src', 'dir'), os.path.join(self.tmp, 'dest', 'dir'))

        assert os.listdir(os.path.join(self.tmp, 'dest', 'dir')) == ['keep']


RENAME = os.rename


def rename_across_file_systems(src, dest):
    # only the move of the top dir crosses file systems, the steps stay on one
    if os.path.basename(src) == 'dir' and not os.path.basename(os.path.dirname(dest)).startswith('.trash-cli-'):
        raise OSError(errno.EXDEV, 'Invalid cross-device link', src)
    RENAME(src, dest)
