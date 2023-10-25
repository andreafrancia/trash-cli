from typing import NamedTuple, Optional


class GateCheckResult(NamedTuple('GateCheckResult', [
    ('ok', bool),
    ('reason', Optional[str]),
])):

    @staticmethod
    def make_ok():
        return GateCheckResult(True, None)

    @staticmethod
    def make_error(reason):
        return GateCheckResult(False, reason)

    def __repr__(self):
        if self.ok and self.reason is None:
            return 'GateCheckResult.ok()'
        if not self.ok and self.reason is not None:
            return 'GateCheckResult.error(%r)' % self.reason
        return 'GateCheckResult(%s, %r)' % (self.ok, self.reason)
