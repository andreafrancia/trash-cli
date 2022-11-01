from trashcli.put.gate import Gate


class SameVolumeGate(Gate):
    def can_trash_in(self, trashee, candidate, trash_dir_volume):
        return trash_dir_volume.volume_of_trash_dir(
            candidate.trash_dir_path) == trashee.volume
    def __repr__(self):
        return 'SameVolumeGate()'
    def __eq__(self, other):
        return isinstance(other, SameVolumeGate)
