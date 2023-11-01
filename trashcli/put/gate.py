from enum import Enum


class Gate(Enum):
    HomeFallback = "HomeFallbackGate"
    SameVolume = "SameVolumeGate"

    def __repr__(self):
        return "%s.%s" % (type(self).__name__, self.name)
