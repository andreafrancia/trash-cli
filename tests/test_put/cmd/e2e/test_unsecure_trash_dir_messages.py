# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import os

import pytest

from tests.support.files import make_empty_file
from tests.support.files import make_sticky_dir
from tests.support.files import require_empty_dir
from tests.test_put.cmd.e2e.run_trash_put import run_trashput_with_vol
from tests.support.dirs.temp_dir import temp_dir

temp_dir = temp_dir


@pytest.mark.slow
class TestUnsecureTrashDirMessages:

    @pytest.fixture
    def fake_vol(self, temp_dir):
        return temp_dir / 'fake-vol'

    def test_when_is_unsticky(self, temp_dir, fake_vol):
        require_empty_dir(fake_vol)
        make_empty_file(fake_vol / 'foo')
        require_empty_dir(fake_vol / '.Trash')

        output = run_trashput_with_vol(temp_dir, fake_vol, [fake_vol / 'foo'])

        assert output.grep("/.Trash/123").stream == (
            'trash-put:  `- failed to trash /vol/foo in /vol/.Trash/123, because trash '
            'dir is insecure, its parent should be sticky, trash-dir: /vol/.Trash/123, '
            'parent: /vol/.Trash\n'
        )

    def test_when_it_is_not_a_dir(self, fake_vol, temp_dir):
        require_empty_dir(fake_vol)
        make_empty_file(fake_vol / 'foo')
        make_empty_file(fake_vol / '.Trash')

        output = run_trashput_with_vol(temp_dir, fake_vol, [fake_vol / 'foo'])

        assert output.grep("/.Trash/123").stream == (
            'trash-put:  `- failed to trash /vol/foo in /vol/.Trash/123, because trash '
            'dir cannot be created as its parent is a file instead of being a directory, '
            'trash-dir: /vol/.Trash/123, parent: /vol/.Trash\n'
        )

    def test_when_is_a_symlink(self, fake_vol, temp_dir):
        require_empty_dir(fake_vol)
        make_empty_file(fake_vol / 'foo')
        make_sticky_dir(fake_vol / 'link-destination')
        os.symlink('link-destination', fake_vol / '.Trash')

        output = run_trashput_with_vol(temp_dir, fake_vol, [fake_vol / 'foo'])

        assert output.grep("insecure").stream == (
            'trash-put:  `- failed to trash /vol/foo in /vol/.Trash/123, because '
            'trash dir is insecure, its parent should not be a symlink, trash-dir: '
            '/vol/.Trash/123, parent: /vol/.Trash\n')
