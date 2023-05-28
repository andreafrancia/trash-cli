from typing import Union, Type

import six

from trashcli.put.class_name_meta import ClassNameMeta


@six.add_metaclass(ClassNameMeta)
class ClosedGate:
    pass


@six.add_metaclass(ClassNameMeta)
class HomeFallbackGate:
    pass


@six.add_metaclass(ClassNameMeta)
class SameVolumeGate:
    pass


Gate = Union[
    Type[ClosedGate],
    Type[HomeFallbackGate],
    Type[SameVolumeGate],
]
