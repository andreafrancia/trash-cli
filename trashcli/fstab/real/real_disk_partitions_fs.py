from typing import Any, List

from trashcli.fstab.protocols.disk_partitions_fs import DiskPartitionsFs


class RealDiskPartitionsFs(DiskPartitionsFs):
    def disk_partitions(self,
                        all,  # type: bool
                        ):  # type: (...) -> List[Any]
        import psutil
        return psutil.disk_partitions(all=all)
