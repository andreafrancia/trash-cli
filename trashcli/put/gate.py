import six
from trashcli.put.class_name_meta import ClassNameMeta


class Gate(object):
    pass


@six.add_metaclass(ClassNameMeta)
class ClosedGate(Gate):
    pass


@six.add_metaclass(ClassNameMeta)
class HomeFallbackGate(Gate):
    pass


@six.add_metaclass(ClassNameMeta)
class SameVolumeGate(Gate):
    pass
