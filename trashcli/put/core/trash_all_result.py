from typing import NamedTuple, List


class TrashAllResult(NamedTuple('TrashAllResult', [
    ('failed_paths', List[str]),
])):
    def any_failure(self):  # type: () -> bool
        return len(self.failed_paths) > 0
