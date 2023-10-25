import unittest

from trashcli.put.trashing_checker import GateCheckResult


class TestGateCheckResult(unittest.TestCase):

    def test_equality(self):
        a = GateCheckResult(True, 'msg')
        b = GateCheckResult(True, 'msg')

        assert a == b

    def test_not_equals_by_ok(self):
        a = GateCheckResult(True, 'msg')
        b = GateCheckResult(False, 'msg')

        assert a != b

    def test_not_equals_by_string(self):
        a = GateCheckResult(True, 'msg1')
        b = GateCheckResult(True, 'msg2')

        assert a != b
