import sys
from io import StringIO
from typing import Dict

from tests.support.run_command import CmdResult
from trashcli.fstab.volumes import Volumes
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.file_system import FakeReadCwd, FileReader, \
    RestoreReadFileSystem, \
    RestoreWriteFileSystem, ListingFileSystem
from trashcli.restore.info_dir_searcher import InfoDirSearcher
from trashcli.restore.info_files import InfoFiles
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trash_directories import TrashDirectoriesImpl
from trashcli.restore.trashed_files import TrashedFiles


class MemoLogger:
    def __init__(self):
        self.messages = []

    def warning(self, msg):
        self.messages.append("warning: " + msg)


class RestoreUser:
    def __init__(self,
                 environ,  # type: Dict[str, str]
                 uid,  # type: int
                 file_reader,  # type: FileReader
                 read_fs,  # type: RestoreReadFileSystem
                 write_fs,  # type: RestoreWriteFileSystem
                 listing_file_system,  # type: ListingFileSystem
                 version,  # type: str
                 volumes,  # type: Volumes
                 ):
        self.environ = environ
        self.uid = uid
        self.file_reader = file_reader
        self.read_fs = read_fs
        self.write_fs = write_fs
        self.listing_file_system = listing_file_system
        self.version = version
        self.volumes = volumes

    no_args = object()

    def run_restore(self, args=no_args, reply='', from_dir=None):
        args = [] if args is self.no_args else args
        stdout = StringIO()
        stderr = StringIO()
        read_cwd = FakeReadCwd(from_dir)
        logger = MemoLogger()
        trash_directories = TrashDirectoriesImpl(self.volumes,
                                                 self.uid,
                                                 self.environ)
        searcher = InfoDirSearcher(trash_directories,
                                   InfoFiles(self.listing_file_system))
        trashed_files = TrashedFiles(logger,
                                     self.file_reader,
                                     searcher)
        cmd = RestoreCmd.make(stdout=stdout,
                              stderr=stderr,
                              exit=sys.exit,
                              input=HardCodedInput(reply),
                              version=self.version,
                              trashed_files=trashed_files,
                              read_fs=self.read_fs,
                              write_fs=self.write_fs,
                              read_cwd=read_cwd)

        try:
            exit_code = cmd.run(args)
        except SystemExit as e:
            exit_code = e.code

        return CmdResult(stdout.getvalue(),
                         stderr.getvalue(), exit_code)
