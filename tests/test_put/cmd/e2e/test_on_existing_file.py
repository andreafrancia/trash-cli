# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy

import pytest

from tests.support.dirs.support_fs import SupportFs
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.test_put.cmd.e2e.run_trash_put import run_trash_put2
from tests.support.files import fsx

fsx = fsx  # the fixture, imported from its module

temp_dir = temp_dir_fixture


@pytest.fixture
def support_fs(temp_dir):
    return SupportFs(temp_dir.fs, temp_dir)


@pytest.mark.slow
class TestOnExistingFile:
    def test_it_should_be_trashed(self, temp_dir, fsx, support_fs):
        fsx.make_empty_file(temp_dir / 'foo')

        result = run_trash_put2(temp_dir, [temp_dir / "foo"],
                                self._with_xdg_data_dir(temp_dir))

        status = self._status_of_trash(support_fs) + result.status()

        assert ("\n".join(status) ==
                "\n".join([
                    '/foo: does not exist',
                    '/XDG_DATA_HOME/Trash/info/foo.trashinfo: exists',
                    '/XDG_DATA_HOME/Trash/files/foo: exists',
                    'output is empty',
                    'exit code is 0',
                ]))

    @staticmethod
    def _status_of_trash(support_fs):
        return support_fs.existence_of(
            'foo',
            'XDG_DATA_HOME/Trash/info/foo.trashinfo',
            'XDG_DATA_HOME/Trash/files/foo')

    @staticmethod
    def _with_xdg_data_dir(temp_dir):
        return {'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME'}
