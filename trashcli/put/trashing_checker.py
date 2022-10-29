from trashcli.put.candidate import Candidate
from trashcli.put.trashee import Trashee


class TrashingChecker:
    def __init__(self, trash_dir_volume):
        self.trash_dir_volume = trash_dir_volume

    def file_could_be_trashed_in(self,
                                 trashee,  # type: Trashee
                                 candidate,  # type: Candidate,
                                 ):
        volume_of_trash_dir = self.trash_dir_volume. \
            volume_of_trash_dir(candidate.trash_dir_path)

        return volume_of_trash_dir == trashee.volume
