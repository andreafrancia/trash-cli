# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os
from os.path import exists as file_exists
from typing import List
from typing import Optional

import pytest

from tests import run_command
from tests.run_command import run_trash_put_in_tmp_dir
from tests.run_command import temp_dir  # noqa
from tests.support.files import make_empty_file
from tests.support.files import make_sticky_dir
from tests.support.files import require_empty_dir
from trashcli.fs import read_file
from trashcli.lib.environ import Environ


@pytest.fixture
def runner(temp_dir):
    return Runner(temp_dir)


class Runner:
    def __init__(self, cwd):
        self.cwd = cwd

    def run_trashput(self,
                     args,  # type: List[str]
                     env=None,  # type: Optional[Environ]
                     ):  # type: (...) -> run_command.CmdResult
        env = env or {}
        env['TRASH_PUT_FAKE_UID_FOR_TESTING'] = '123'
        return run_command.run_command(self.cwd,
                                       "trash-put",
                                       list(args),
                                       env=env)

    def run_trashput2(self,
                      args,  # type: List[str]
                      env=None,  # type: Optional[Environ]
                      ):  # type: (...) -> run_command.PutResult
        return run_trash_put_in_tmp_dir(self.cwd, args)


@pytest.mark.slow
class TestDeletingExistingFile:

    @pytest.fixture
    def trash_foo(self, temp_dir, runner):
        make_empty_file(temp_dir / 'foo')
        result = runner.run_trashput([temp_dir / 'foo'], env={
            'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME'})
        yield result

    def test_it_should_remove_the_file(self, temp_dir, trash_foo):
        assert file_exists(temp_dir / 'foo') is False

    def test_it_should_remove_it_silently(self, trash_foo):
        assert trash_foo.stdout == ''

    def test_a_trashinfo_file_should_have_been_created(self, temp_dir,
                                                       trash_foo):
        read_file(temp_dir / 'XDG_DATA_HOME/Trash/info/foo.trashinfo')


@pytest.mark.slow
class TestWhenDeletingAnExistingFileInVerboseMode:
    @pytest.fixture
    def run_trashput(self, temp_dir, runner):
        make_empty_file(temp_dir / "foo")
        return runner.run_trashput(["-v", temp_dir / "foo"], env={
            'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME',
            'HOME': temp_dir / 'home'})

    def test_should_tell_where_a_file_is_trashed(self, temp_dir, run_trashput):
        output = run_trashput.clean_tmp_and_grep(temp_dir, "trashed in")

        assert "trash-put: '/foo' trashed in /XDG_DATA_HOME/Trash" in output.splitlines()

    def test_should_be_successful(self, run_trashput):
        assert 0 == run_trashput.exit_code


@pytest.mark.slow
class TestUnsecureTrashDirMessages:

    @pytest.fixture
    def fake_vol(self, temp_dir):
        vol = temp_dir / 'fake-vol'
        require_empty_dir(vol)
        return vol

    def test_when_is_unsticky(self, temp_dir, fake_vol, runner):
        make_empty_file(fake_vol / 'foo')
        require_empty_dir(fake_vol / '.Trash')

        result = runner.run_trashput(['--force-volume',
                                      fake_vol,
                                      '-v',
                                      fake_vol / 'foo'])

        assert result.clean_vol_and_grep('/.Trash/123', fake_vol) == [
            'trash-put:  `- failed to trash /vol/foo in /vol/.Trash/123, because trash '
            'dir is insecure, its parent should be sticky, trash-dir: /vol/.Trash/123, '
            'parent: /vol/.Trash'
        ]

    def test_when_it_is_not_a_dir(self, fake_vol, runner, temp_dir):
        make_empty_file(fake_vol / 'foo')
        make_empty_file(fake_vol / '.Trash')

        result = runner.run_trashput(['--force-volume',
                                      fake_vol,
                                      '-v',
                                      fake_vol / 'foo'])

        assert result.clean_vol_and_grep('/.Trash/123', fake_vol) == [
            'trash-put:  `- failed to trash /vol/foo in /vol/.Trash/123, because trash '
            'dir cannot be created as its parent is a file instead of being a directory, '
            'trash-dir: /vol/.Trash/123, parent: /vol/.Trash'
        ]

    def test_when_is_a_symlink(self, fake_vol, temp_dir, runner):
        make_empty_file(fake_vol / 'foo')
        make_sticky_dir(fake_vol / 'link-destination')
        os.symlink('link-destination', fake_vol / '.Trash')

        result = runner.run_trashput(['--force-volume',
                                      fake_vol, '-v', fake_vol / 'foo'])

        assert result.clean_vol_and_grep("insecure", fake_vol) == [
            'trash-put:  `- failed to trash /vol/foo in /vol/.Trash/123, because '
            'trash dir is insecure, its parent should not be a symlink, trash-dir: '
            '/vol/.Trash/123, parent: /vol/.Trash']
