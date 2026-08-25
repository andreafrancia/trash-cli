import sys


def protocol():
    try:
        from typing import Protocol
        return Protocol
    except ImportError as e:
        from typing_extensions import Protocol
        return Protocol


Protocol = protocol()

del protocol

if sys.version_info[0] >= 3:
    # python 3: go between str paths and their raw bytes
    from os import fsencode
    from os import fsdecode
else:
    # python 2: paths are plain byte strings already
    def fsencode(path):
        return path

    def fsdecode(path):
        return path
