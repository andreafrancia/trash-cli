import pytest

from tests.run_command import temp_dir  # noqa
from tests.support.files import make_empty_file
from tests.test_put.test_e2e.run_trash_put import run_trash_put2


@pytest.mark.slow
class TestOnTrashingAFile:

    def test_in_verbose_mode_should_tell_where_a_file_is_trashed(self, temp_dir):
        env = {'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME',
               'HOME': temp_dir / 'home'}
        make_empty_file(temp_dir / "foo")

        result = run_trash_put2(temp_dir, ["-v", temp_dir / "foo"], env)

        assert [result.both().cleaned(), result.exit_code] == [
            "trash-put: '/foo' trashed in /XDG_DATA_HOME/Trash\n",
            0
        ]

