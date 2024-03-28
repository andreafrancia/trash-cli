from typing import NamedTuple

from tests.run_command import grep
from tests.support.my_path import MyPath


class Stream(NamedTuple('Output', [
    ('stream', str),
    ('temp_dir', MyPath)
])):
    def lines(self):
        return self.stream.replace(self.temp_dir, '').splitlines()

    def last_line(self):
        return self.lines()[-1]

    def first_line(self):
        return self.lines()[0]

    def cleaned(self):
        return self.stream.replace(self.temp_dir, '')

    def describe_stream(self):  # type: () -> str
        if len(self.stream) == 0:
            return "empty"
        else:
            return repr(self.stream)

    def grep(self, pattern):
        return Stream(stream=grep(self.stream, pattern),
                      temp_dir=self.temp_dir)

    def replace(self, old, new):
        return Stream(stream=self.stream.replace(old, new),
                      temp_dir=self.temp_dir)
