from typing import List
from typing import Tuple

from tests.test_put.support.logs import Logs
from trashcli.put.core.logs import LogTag


class Result:
    def __init__(self,
                 stderr,  # type: List[str]
                 err,  # type: str
                 exit_code,  # type: int
                 collected_logs,  # type: Logs
                 ):
        self.stderr = stderr
        self.err = err
        self.exit_code = exit_code
        self.collected_logs = collected_logs

    def exit_code_and_stderr(self):
        return [self.exit_code,
                self.stderr]

    def exit_code_and_logs(self,
                           log_tag,  # type: LogTag
                           ):  # type: (...) -> Tuple[int, List[str]]
        return (self.exit_code,
                self.collected_logs.with_tag(log_tag))
