from mock import Mock
import pytest

from tests.fake_trash_dir import FakeTrashDir
from tests.output_collector import OutputCollector
from tests.run_command import temp_dir  # noqa
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
    def __init__(self, xdg_data_home):
        self.xdg_data_home = xdg_data_home
        self.environ = {'XDG_DATA_HOME': xdg_data_home}
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
        return RunResult(clean(stdout.getvalue(), self.xdg_data_home),
                         clean(stderr.getvalue(), self.xdg_data_home))

    def set_fake_uid(self, uid):
        self.fake_uid = uid

    def add_volume(self, mount_point):
        self.volumes.append(mount_point)

    def top1(self, top_dir):
        return FakeTrashDir(top_dir / '.Trash/123')

    def top2(self, top_dir):
        return FakeTrashDir(top_dir / '.Trash-123')

    def home(self):
        return FakeTrashDir(self.xdg_data_home / "Trash")

    def set_version(self, version):
        self.version = version


def clean(stream, xdg_data_home):
    return stream.replace(xdg_data_home, 'XDG_DATA_HOME')
