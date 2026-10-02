# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
from trashcli.compat import Protocol


class MountPointListFs(Protocol):
    def list_mount_points(self):
        raise NotImplementedError()
