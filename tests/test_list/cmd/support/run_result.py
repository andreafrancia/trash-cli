from typing import NamedTuple


class RunResult(NamedTuple("RunResult", [
    ('stdout', str),
    ('stderr', str),
])):
    def whole_output(self):
        return self.stderr + self.stdout
