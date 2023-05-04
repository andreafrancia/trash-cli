import os

from mock import Mock

from tests.fake_trash_dir import FakeTrashDir
from tests.output_collector import OutputCollector
from tests.support.fake_volume_of import volume_of_stub
from trashcli.file_system_reader import FileSystemReader
from trashcli.fstab.volume_listing import VolumesListing
from trashcli.list.main import ListCmd


class TrashListUser:
    def __init__(self, xdg_data_home):
        self.stdout = OutputCollector()
        self.stderr = OutputCollector()
        self.environ = {'XDG_DATA_HOME': xdg_data_home}
        self.fake_uid = None
        self.volumes = []
        trash_dir = os.path.join(xdg_data_home, "Trash")
        self.home_trashdir = FakeTrashDir(trash_dir)
        self.version = None

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
            volumes_listing=volumes_listing,
            uid=self.fake_uid,
            volumes=volume_of_stub(),
            file_reader=file_reader,
            version=self.version
        ).run(argv)

    def set_fake_uid(self, uid):
        self.fake_uid = uid

    def add_volume(self, mount_point):
        self.volumes.append(mount_point)

    def error(self):
        return self.stderr.getvalue()

    def output(self):
        return self.stdout.getvalue()

    def set_version(self, version):
        self.version = version
