# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy

import pytest

from tests.support.dirs.temp_dir import temp_dir
from tests.support.fs_fixture import FsFixture
from tests.test_put.cmd.e2e.run_trash_put import run_trash_put2
from trashcli.put.fs.real_fs import RealFs

temp_dir = temp_dir


@pytest.mark.slow
class TestOnExistingFile:
    def setup_method(self, method):
        self.fx = FsFixture(RealFs())

    def test_it_should_be_trashed(self, temp_dir):
        self.fx.make_empty_file(temp_dir / 'foo')

        result = run_trash_put2(temp_dir, [temp_dir / "foo"],
                                self._with_xdg_data_dir(temp_dir))

        assert self._status_of_trash(temp_dir) + result.status() == [
            '/foo: does not exist',
            '/XDG_DATA_HOME/Trash/info/foo.trashinfo: exists',
            '/XDG_DATA_HOME/Trash/files/foo: exists',
            'output is empty',
            'exit code is 0',
        ]

    @staticmethod
    def _status_of_trash(temp_dir):
        return temp_dir.existence_of('foo',
                                     'XDG_DATA_HOME/Trash/info/foo.trashinfo',
                                     'XDG_DATA_HOME/Trash/files/foo')

    @staticmethod
    def _with_xdg_data_dir(temp_dir):
        return {'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME'}
