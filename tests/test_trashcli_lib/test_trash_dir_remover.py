import os
import shutil
import tempfile

import pytest

from trashcli.lib import trash_dir_remover
from trashcli.lib.trash_dir_remover import remove_in_trash_dir


class TestRemoveInTrashDir:
    def setup_method(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.trash = os.path.join(self.tmp, 'Trash')
        os.makedirs(os.path.join(self.trash, 'files', 'dir', 'sub'))
        open(os.path.join(self.trash, 'files', 'dir', 'sub', 'file'), 'w').close()
        open(os.path.join(self.trash, 'files', 'x'), 'w').close()
        os.makedirs(os.path.join(self.tmp, 'outside'))
        open(os.path.join(self.tmp, 'outside', 'x'), 'w').close()
        self.cwd = os.getcwd()

    def teardown_method(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def test_a_file_and_a_dir_tree_are_removed(self):
        remove_in_trash_dir(self.trash, os.path.join(self.trash, 'files', 'x'))
        remove_in_trash_dir(self.trash, os.path.join(self.trash, 'files', 'dir'))

        assert os.listdir(os.path.join(self.trash, 'files')) == []
        assert os.getcwd() == self.cwd

    def test_a_files_dir_that_leads_elsewhere_is_refused(self):
        shutil.rmtree(os.path.join(self.trash, 'files'))
        os.symlink(os.path.join(self.tmp, 'outside'), os.path.join(self.trash, 'files'))

        with pytest.raises(OSError):
            remove_in_trash_dir(self.trash, os.path.join(self.trash, 'files', 'x'))

        assert os.listdir(os.path.join(self.tmp, 'outside')) == ['x']

    def test_a_dir_swapped_for_a_symlink_while_removing_is_refused(self, monkeypatch):
        chdir = os.chdir

        def swap_then_chdir(path):
            if path == 'sub':
                shutil.rmtree('sub')
                os.symlink(os.path.join(self.tmp, 'outside'), 'sub')
            chdir(path)

        monkeypatch.setattr(trash_dir_remover.os, 'chdir', swap_then_chdir)

        with pytest.raises(OSError):
            remove_in_trash_dir(self.trash, os.path.join(self.trash, 'files', 'dir'))

        assert os.listdir(os.path.join(self.tmp, 'outside')) == ['x']

    def test_a_relative_trash_dir_works(self):
        os.chdir(self.tmp)

        remove_in_trash_dir('Trash', 'Trash/files/x')

        assert sorted(os.listdir(os.path.join(self.trash, 'files'))) == ['dir']

    def test_an_own_symlink_to_the_trash_dir_is_followed(self):
        link = os.path.join(self.tmp, 'link')
        os.symlink(self.trash, link)

        remove_in_trash_dir(link, os.path.join(link, 'files', 'x'))

        assert sorted(os.listdir(os.path.join(self.trash, 'files'))) == ['dir']
