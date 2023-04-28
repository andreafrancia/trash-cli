import os
from mock import Mock

from tests.fake_trash_dir import FakeTrashDir
from trashcli.fs import FileSystemReader
from trashcli.fstab import VolumesListing
from trashcli.list.main import ListCmd
from tests.output_collector import OutputCollector
from tests.support.volumes_mock import volumes_mock


class TrashListUser:
    def __init__(self, xdg_data_home):
        self.stdout = OutputCollector()
        self.stderr = OutputCollector()
        self.environ = {'XDG_DATA_HOME': xdg_data_home}
        self.fake_uid = None
        self.volumes = []
        trash_dir = os.path.join(xdg_data_home, "Trash")
        self.home_trashdir = FakeTrashDir(trash_dir)

    def run_trash_list(self, *args):
        self.run('trash-list', *args)

    def run(self, *argv):
        file_reader = FileSystemReader()
        file_reader.list_volumes = lambda: self.volumes
        volumes_listing = Mock(spec=VolumesListing)
        volumes_listing.list_volumes.return_value = self.volumes
        ListCmd(
            out=self.stdout,
            err=self.stderr,
            environ=self.environ,
            uid=self.fake_uid,
            file_reader=file_reader,
            volumes_listing=volumes_listing,
            volumes=volumes_mock()
        ).run(argv)

    def set_fake_uid(self, uid):
        self.fake_uid = uid

    def add_volume(self, mount_point):
        self.volumes.append(mount_point)

    def error(self):
        return self.stderr.getvalue()

    def output(self):
        return self.stdout.getvalue()
