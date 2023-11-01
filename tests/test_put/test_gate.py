from trashcli.put.gate import Gate


class TestGate:
    def test_gate(self):
        assert repr(Gate.SameVolume) == 'Gate.SameVolume'
        assert str(Gate.SameVolume) == 'Gate.SameVolume'
        assert repr(Gate.HomeFallback) == 'Gate.HomeFallback'
        assert str(Gate.HomeFallback) == 'Gate.HomeFallback'
