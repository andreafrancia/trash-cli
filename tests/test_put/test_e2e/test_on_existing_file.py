# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy

import pytest

from tests.run_command import run_trash_put2
from tests.run_command import temp_dir  # noqa
from tests.support.files import make_empty_file


@pytest.mark.slow
class TestOnExistingFile:
    def test_it_should_be_trashed(self, temp_dir):
        make_empty_file(temp_dir / 'foo')

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
