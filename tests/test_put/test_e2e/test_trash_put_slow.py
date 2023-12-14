# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os
from typing import List
from typing import Optional

import pytest

from tests import run_command
from tests.run_command import temp_dir  # noqa
from tests.support.files import make_empty_file
from tests.support.files import make_sticky_dir
from tests.support.files import require_empty_dir
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
