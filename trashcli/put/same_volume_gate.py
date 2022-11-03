import six

from trashcli.put.class_name_meta import ClassNameMeta
from trashcli.put.gate import Gate


@six.add_metaclass(ClassNameMeta)
class ClosedGate(Gate):
    @staticmethod
    def can_trash_in(trashee, candidate, trash_dir_volume):
        return False


@six.add_metaclass(ClassNameMeta)
class SameVolumeGate(Gate):
    @staticmethod
    def can_trash_in(trashee, candidate, trash_dir_volume):
        return trash_dir_volume.volume_of_trash_dir(
            candidate.trash_dir_path) == trashee.volume
