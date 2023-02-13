import os
import unittest
from pprint import pprint

from .support.fake_fs.fake_fs import FakeFs
from trashcli.put.candidate import Candidate
from trashcli.put.gate import HomeFallbackGate
from trashcli.put.gate_impl import HomeFallbackGateImpl, GateCheckResult
from trashcli.put.path_maker import AbsolutePaths
from trashcli.put.security_check import NoCheck
from trashcli.put.trashee import Trashee


class TestHomeFallbackGateImpl(unittest.TestCase):
    def setUp(self):
        self.fake_fs = FakeFs()
        self.gate_impl = HomeFallbackGateImpl(self.fake_fs)

    def test_not_enabled(self):
        result = self.gate_impl.can_trash_in(make_trashee(),
                                             make_candidate('/xdf/Trash'),
                                             {})
        assert [result] == [
            GateCheckResult.make_error('trash dir not enabled: /xdf/Trash')]

    def test_enabled(self):
        result = self.gate_impl.can_trash_in(make_trashee(),
                                             make_candidate('/xdf/Trash'),
                                             {
                                                 "TRASH_ENABLE_HOME_FALLBACK": "1"
                                             })
        assert [result] == [
            GateCheckResult.make_ok()]

    # def test(self):
    #     result = os.statvfs('/Users/andrea/trash-cli')
    #     print("")
    #     pprint(result.f_bavail / 1024 / 1024)
    #     pprint(result.f_bfree / 1024 / 1024)
    #     # pprint(psutil.disk_usage('/'))


def make_candidate(path):
    return Candidate(path, '/disk2', AbsolutePaths, NoCheck,
                     HomeFallbackGate)


def make_trashee():
    return Trashee('/disk1/foo', "/disk1")
