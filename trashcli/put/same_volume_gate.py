from trashcli.put.gate import Gate


class SameVolumeGate(Gate):
    @staticmethod
    def can_trash_in(trashee, candidate, trash_dir_volume):
        return trash_dir_volume.volume_of_trash_dir(
            candidate.trash_dir_path) == trashee.volume
