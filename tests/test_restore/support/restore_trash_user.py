import os
from io import StringIO

from mock import Mock

from tests.fake_trash_dir import trashinfo_content_default_date
from tests.support.files import make_file
from trashcli.fs import remove_file
from trashcli.fstab.volumes import RealVolumes
from trashcli.list_mount_points import FakeMountPointsListing
from trashcli.restore.file_system import RealRestoreWriteFileSystem, \
    FakeReadCwd, RealRestoreReadFileSystem, RealFileReader, ListingFileSystem
from trashcli.restore.info_dir_searcher import InfoDirSearcher
from trashcli.restore.info_files import InfoFiles
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trash_directories import TrashDirectoriesImpl
from trashcli.restore.trashed_file import TrashedFiles


class RestoreTrashUser:
    def __init__(self, XDG_DATA_HOME, cwd):
        self.XDG_DATA_HOME = XDG_DATA_HOME
        self.out = StringIO()
        self.err = StringIO()
        self.cwd = cwd
        self.read_fs = RealRestoreReadFileSystem()
        self.read_cwd = FakeReadCwd(cwd)
        self.write_fs = RealRestoreWriteFileSystem()

    def chdir(self, dir):
        self.current_dir = dir
        self.read_cwd.chdir(dir)

    def run_restore(self, with_user_typing=''):
        environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME}
        trash_directories = TrashDirectoriesImpl(FakeMountPointsListing([]),
                                                 RealVolumes(),
                                                 os.getuid(),
                                                 environ)
        logger = Mock(spec=[])
        searcher = InfoDirSearcher(trash_directories, InfoFiles(ListingFileSystem()))
        trashed_files = TrashedFiles(logger,
                                     RealFileReader(),
                                     searcher)
        RestoreCmd.make(
            stdout=self.out,
            stderr=self.err,
            exit=[].append,
            input=lambda msg: with_user_typing,
            version='0.0.0',
            trashed_files=trashed_files,
            read_fs=self.read_fs,
            write_fs=self.write_fs,
            read_cwd=FakeReadCwd(self.current_dir)
        ).run([])

    def having_a_file_trashed_from_current_dir(self, filename):
        self.having_a_trashed_file(os.path.join(self.cwd, filename))
        remove_file(filename)
        assert not os.path.exists(filename)

    def having_a_trashed_file(self, path):
        make_file('%s/info/foo.trashinfo' % self._trash_dir(),
                  trashinfo_content_default_date(path))
        make_file('%s/files/foo' % self._trash_dir())

    def _trash_dir(self):
        return "%s/Trash" % self.XDG_DATA_HOME

    def stdout(self):
        return self.out.getvalue()

    def stderr(self):
        return self.err.getvalue()
