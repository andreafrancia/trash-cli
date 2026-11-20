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

    def test_a_file_written_during_the_copy_is_not_lost(self, monkeypatch):
        src, dest = self.writable_across_file_systems(monkeypatch)
        copytree = real_move.shutil.copytree

        def copy_while_another_program_writes(a, b, *args, **kwargs):
            copytree(a, b, *args, **kwargs)
            if a == src:
                open(os.path.join(src, 'new'), 'w').close()

        monkeypatch.setattr(real_move.shutil, 'copytree', copy_while_another_program_writes)

        with pytest.raises(OSError):
            RealMove().move(src, dest)

        assert sorted(os.listdir(src)) == ['new', 'sub']
        assert not os.path.exists(dest)

    def test_removed_dirs_are_put_back_after_a_failure(self, monkeypatch):
        src, dest = self.writable_across_file_systems(monkeypatch)
        rmdir = os.rmdir

        def the_last_step_fails(path, *args, **kwargs):
            if path == src:
                raise OSError(errno.EACCES, 'Permission denied', path)
            rmdir(path, *args, **kwargs)

        monkeypatch.setattr(real_move.os, 'rmdir', the_last_step_fails)

        with pytest.raises(OSError):
            RealMove().move(src, dest)

        assert os.path.exists(os.path.join(src, 'sub', 'file'))
        assert not os.path.exists(dest)

    def test_a_destination_created_just_before_the_copy_is_kept(self, monkeypatch):
        src, dest = self.writable_across_file_systems(monkeypatch)
        copytree = real_move.shutil.copytree

        def another_program_creates_the_destination(a, b, *args, **kwargs):
            if a == src:
                os.mkdir(b)
                open(os.path.join(b, 'theirs'), 'w').close()
            copytree(a, b, *args, **kwargs)

        monkeypatch.setattr(real_move.shutil, 'copytree', another_program_creates_the_destination)

        with pytest.raises(OSError):
            RealMove().move(src, dest)

        assert os.listdir(dest) == ['theirs']
        assert os.path.exists(os.path.join(src, 'sub', 'file'))

    def writable_across_file_systems(self, monkeypatch):
        src = os.path.join(self.tmp, 'src', 'dir')
        os.chmod(src, 0o755)
        monkeypatch.setattr(real_move.os, 'rename', rename_across_file_systems)
        return src, os.path.join(self.tmp, 'dest', 'dir')


RENAME = os.rename


def rename_across_file_systems(src, dest):
    # only the move of the top dir crosses file systems, the steps stay on one
    if os.path.basename(src) == 'dir' and not os.path.basename(os.path.dirname(dest)).startswith('.trash-cli-'):
        raise OSError(errno.EXDEV, 'Invalid cross-device link', src)
    RENAME(src, dest)
