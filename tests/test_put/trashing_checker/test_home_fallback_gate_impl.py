from trashcli.put.candidate import Candidate
from trashcli.put.core.path_maker_type import PathMakerType
from trashcli.put.gate import Gate
from trashcli.put.security_check import NoCheck
from trashcli.put.trashee import Trashee
from trashcli.put.trashing_checker import make_ok, \
    make_error, TrashDirChecker
from ..support.fake_fs.fake_fs import FakeFs


class TestHomeFallbackGate:
    def setup_method(self):
        self.fake_fs = FakeFs()
        self.gate_impl = TrashDirChecker(self.fake_fs, "volumes")

    def test_not_enabled(self):
        result = self.gate_impl.file_could_be_trashed_in(
            make_trashee(),
            make_candidate('/xdf/Trash'),
            {})
        assert [result] == [make_error('trash dir not enabled: /xdf/Trash')]

    def test_enabled(self):
        result = self.gate_impl.file_could_be_trashed_in(
            make_trashee(),
            make_candidate('/xdf/Trash'),
            {
                "TRASH_ENABLE_HOME_FALLBACK": "1"
            })
        assert [result] == [make_ok()]

    # def test(self):
    #     result = os.statvfs('/Users/andrea/trash-cli')
    #     print("")
    #     pprint(result.f_bavail / 1024 / 1024)
    #     pprint(result.f_bfree / 1024 / 1024)
    #     # pprint(psutil.disk_usage('/'))


def make_candidate(path):
    return Candidate(path, '/disk2', PathMakerType.AbsolutePaths, NoCheck,
                     Gate.HomeFallback)


def make_trashee():
    return Trashee('/disk1/foo', "/disk1")
