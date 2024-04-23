from typing import NamedTuple

from tests.support.text.sort_lines import sort_lines


class RunResult(NamedTuple("RunResult", [
    ('stdout', str),
    ('stderr', str),
])):
    def whole_output(self):
        return self.stderr + self.stdout

    def sorted_whole_output(self):
        return sort_lines(self.whole_output())

    def all_lines(self):
        return set(self.whole_output().splitlines())

    def err_and_out(self):
        return self.stderr, self.stdout
