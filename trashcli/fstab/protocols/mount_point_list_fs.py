# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
from typing import List

from trashcli.compat import Protocol


class MountPointListFs(Protocol):
    def list_mount_points(self):  # type: () -> List[str]
        raise NotImplementedError
