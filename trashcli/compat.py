def protocol():
    try:
        from typing import Protocol
        return Protocol
    except ImportError as e:
        from typing_extensions import Protocol
        return Protocol


Protocol = protocol()

del protocol
