from mock import Mock
import pytest

from tests.support.fake_trash_dir import FakeTrashDir
from tests.support.files import make_empty_dir
from tests.support.output_collector import OutputCollector
from tests.support.fake_volume_of import volume_of_stub
from tests.support.my_path import MyPath
from trashcli.empty.main import FileSystemContentReader
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirRulesReader
from trashcli.file_system_reader import FileSystemReader
from trashcli.fstab.volume_listing import VolumesListing
from trashcli.lib.dir_reader import RealDirReader
from trashcli.list.main import ListCmd
from .run_result import RunResult


@pytest.fixture
def trash_list_user():
    temp_dir = MyPath.make_temp_dir()
    yield TrashListUser(temp_dir)
    temp_dir.clean_up()


class TrashListUser:
    def __init__(self, root):
        self.root = root
        self.xdg_data_home = root / 'xdg-data-home'
        self.environ = {'XDG_DATA_HOME': self.xdg_data_home}
        self.fake_uid = None
        self.volumes = []
        self.version = None

    def run_trash_list(self, *args):  # type: (...) -> RunResult
        file_reader = FileSystemReader()
        file_reader.list_volumes = lambda: self.volumes
        volumes_listing = Mock(spec=VolumesListing)
        volumes_listing.list_volumes.return_value = self.volumes
        stdout = OutputCollector()
        stderr = OutputCollector()
        ListCmd(
            out=stdout,
            err=stderr,
            environ=self.environ,
            volumes_listing=volumes_listing,
            uid=self.fake_uid,
            volumes=volume_of_stub(),
            dir_reader=RealDirReader(),
            file_reader=RealTopTrashDirRulesReader(),
            content_reader=FileSystemContentReader(),
            version=self.version
        ).run(['trash-list'] + list(args))
        return RunResult(clean(stdout.getvalue(), self.root),
                         clean(stderr.getvalue(), self.root))

    def set_fake_uid(self, uid):
        self.fake_uid = uid

    def add_volume(self, mount_point):
        self.volumes.append(mount_point)

    def add_disk(self, disk_name):
        top_dir = self.root / disk_name
        make_empty_dir(top_dir)
        self.add_volume(top_dir)
        return top_dir

    def trash_dir1(self, disk_name):
        return FakeTrashDir(self._trash_dir1_parent(disk_name) / '123')

    def trash_dir2(self, disk_name):
        return FakeTrashDir(self.root / disk_name / '.Trash-123')

    def _trash_dir1_parent(self, disk_name):
        return self.root / disk_name / '.Trash'

    def home_trash_dir(self):
        return FakeTrashDir(self.xdg_data_home / "Trash")

    def set_version(self, version):
        self.version = version


def clean(stream, xdg_data_home):
    return stream.replace(xdg_data_home, '')
