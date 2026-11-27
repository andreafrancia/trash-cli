# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
from typing import Dict

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.dirs.support_fs import SupportFs
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.test_put.cmd.e2e.run_trash_put import run_trash_put2
from tests.support.fs_fixture import fsx_fixture, real_fs_fixture, FsFixture
from tests.support.fs_fixture import support_fs_fixture

fs = real_fs_fixture
fsx = fsx_fixture
temp_dir = temp_dir_fixture
support_fs = support_fs_fixture


@pytest.mark.slow
class TestOnExistingFile:
    def test_it_should_be_trashed(self,
                                  temp_dir,  # type: MyPath
                                  fsx,  # type: FsFixture
                                  support_fs,  # type: SupportFs
                                  ):
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
    def _status_of_trash(support_fs,  # type: SupportFs
                         ):
        return support_fs.existence_of(
            'foo',
            'XDG_DATA_HOME/Trash/info/foo.trashinfo',
            'XDG_DATA_HOME/Trash/files/foo')

    @staticmethod
    def _with_xdg_data_dir(temp_dir,  # type: MyPath
                           ):  # type: (...) -> Dict[str, MyPath]
        return {'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME'}
