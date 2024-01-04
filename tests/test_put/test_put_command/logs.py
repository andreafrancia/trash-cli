from typing import List
from typing import NamedTuple

from tests.test_put.test_put_command.log_line import LogLine
from trashcli.put.core.logs import LogTag
from trashcli.put.my_logger import is_right_for_level


class Logs(NamedTuple('Logs', [
    ('logs', List[LogLine])
])):
    def as_stderr_lines(self):
        return ["%s: %s" % (line.program_name, line.message)
                for line in self.logs
                if is_right_for_level(line.verbose, line.level)]

    def with_tag(self,
                 log_tag,  # type: LogTag
                 ):  # type: (...) -> List[str]
        return ["%s" % line.message
                for line in self.logs
                if log_tag == line.tag
                ]


