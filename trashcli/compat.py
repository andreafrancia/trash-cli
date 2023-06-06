def protocol():
    try:
        from typing import Protocol
        return Protocol
    except ImportError as e:
        class Protocol:
            pass

        return Protocol


Protocol = protocol()

del protocol
