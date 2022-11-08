from trashcli.put.gate import SameVolumeGate


class TestGate:
    def test_gate(self):
        a = SameVolumeGate
        assert repr(a) == 'SameVolumeGate'
        assert str(a) == 'SameVolumeGate'
