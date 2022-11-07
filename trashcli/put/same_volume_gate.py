import six

from trashcli.put.class_name_meta import ClassNameMeta
from trashcli.put.gate import Gate, GateCheckResult
from trashcli.put.volume_message_formatter import VolumeMessageFormatter


@six.add_metaclass(ClassNameMeta)
class ClosedGate(Gate):
    @staticmethod
    def can_trash_in(trashee, candidate, trash_dir_volume, environ):
        return GateCheckResult.error("trash dir not enabled: %s" %
                                     candidate.shrink_user(environ))


@six.add_metaclass(ClassNameMeta)
class SameVolumeGate(Gate):
    @staticmethod
    def can_trash_in(trashee, candidate, trash_dir_volume, environ):
        same_volume = trash_dir_volume.volume_of_trash_dir(
            candidate.trash_dir_path) == trashee.volume

        if not same_volume:
            msg_formatter = VolumeMessageFormatter()
            message = msg_formatter.format_msg(trashee, candidate, environ)
            return GateCheckResult.error(message)

        return GateCheckResult.ok()
