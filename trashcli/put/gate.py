class GateCheckResult:
    def __init__(self, ok, reason):
        self.ok = ok
        self.reason = reason

    @staticmethod
    def ok():
        return GateCheckResult(True, None)

    @staticmethod
    def error(reason):
        return GateCheckResult(False, reason)


class Gate(object):
    @staticmethod
    def can_trash_in(trashee,
                     candidate,
                     trash_dir_volume,
                     environ,
                     ):  # type (...) -> bool
        pass
