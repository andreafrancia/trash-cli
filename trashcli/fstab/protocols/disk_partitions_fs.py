from typing import Any, List

from trashcli.compat import Protocol


class DiskPartitionsFs(Protocol):
    def disk_partitions(self,
                        all,  # type: bool
                        ):  # type: (...) -> List[Any]
        raise NotImplementedError()
