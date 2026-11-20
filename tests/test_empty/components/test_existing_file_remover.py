import pytest

from tests.support.fs_fixture import real_fs_fixture
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.real.real_fs import RealFs

fs = real_fs_fixture

@pytest.mark.slow
class TestExistingFileRemover:

    def test_remove_file_if_exists_fails_when_file_does_not_exists(
            self, fs,
    ):  # type: (Fs) -> None
        file_remover = ExistingFileRemover(fs)
        file_remover.remove_file_if_exists('/non/existing/path')
