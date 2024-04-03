import os
from datetime import datetime

from mock import Mock

from tests.fake_trash_dir import FakeTrashDir
from tests.output_collector import OutputCollector
from tests.support.fake_volume_of import volume_of_stub
from trashcli.empty.main import FileSystemContentReader
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirRulesReader
from trashcli.file_system_reader import FileSystemReader
from trashcli.fstab.volume_listing import VolumesListing
from trashcli.lib.dir_reader import RealDirReader
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
        dir_reader = file_reader
        volumes_listing = Mock(spec=VolumesListing)
        volumes_listing.list_volumes.return_value = self.volumes
        ListCmd(
            out=self.stdout,
            err=self.stderr,
            environ=self.environ,
            volumes_listing=volumes_listing,
            uid=self.fake_uid,
            volumes=volume_of_stub(),
            dir_reader=RealDirReader(),
            file_reader=RealTopTrashDirRulesReader(),
            content_reader=FileSystemContentReader(),
            version=self.version
        ).run(argv)

    def set_fake_uid(self, uid):
        self.fake_uid = uid

    def add_volume(self, mount_point):
        self.volumes.append(mount_point)

    def add_trashinfo(self, trash_dir, basename, deletion_date):
        deletion_date = datetime.fromisoformat(deletion_date)
        FakeTrashDir(trash_dir).add_trashinfo2(basename, deletion_date)

    def add_home_trashinfo_without_date(self, basename):
        self.home_trashdir.add_trashinfo_without_date(basename)

    def add_home_trash_with_content(self, basename, content):
        self.home_trashdir.add_trashinfo_content(basename, content)

    def add_unreadable_trashinfo(self, basename):
        self.home_trashdir.add_unreadable_trashinfo(basename)

    def add_trashinfo_without_path(self, basename):
        self.home_trashdir.add_trashinfo_without_path(basename)

    def add_trashinfo_wrong_date(self, basename, wrong_date):
        self.home_trashdir.add_trashinfo_wrong_date(basename, wrong_date)

    def add_home_trashinfo(self,
                           basename,  # type: str
                           deletion_date,  # type: str
                           ):
        deletion_date = datetime.fromisoformat(deletion_date)
        self.home_trashdir.add_trashinfo2(basename, deletion_date)

    def error(self):
        return self.stderr.getvalue()

    def output(self):
        return self.stdout.getvalue()

    def set_version(self, version):
        self.version = version
