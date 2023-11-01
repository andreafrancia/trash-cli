from abc import abstractmethod
from typing import NamedTuple

from trashcli.compat import Protocol
from trashcli.lib.environ import Environ
from trashcli.put.core.candidate import Candidate


class LogContext(NamedTuple('LogContext', [
    ('trashee_path', str),
    ('candidate', Candidate),
    ('environ', Environ),
])):
    def shrunk_candidate_path(self):
        return self.candidate.shrink_user(self.environ)

    def trash_dir_norm_path(self):
        return self.candidate.norm_path()

    def files_dir(self):
        return self.candidate.files_dir()


class FailureReason(Protocol):
    @abstractmethod
    def log_entries(self, context):  # type: (LogContext) -> str
        raise NotImplementedError
