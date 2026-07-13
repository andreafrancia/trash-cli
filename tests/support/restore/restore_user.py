import sys
from io import StringIO
from typing import Dict

from tests.support.run.cmd_result import CmdResult
from tests.test_restore.support.memo_logger import MemoLogger
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fstab.volumes import Volumes
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.file_system import FakeReadCwd, FileReader, \
    RestoreReadFileSystem, \
    RestoreWriteFileSystem, ListingFileSystem
from trashcli.restore.restore_cmd import RestoreCmd

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
                 top_trash_dir_rules_reader=None,
                 ):
        self.environ = environ
        self.uid = uid
        self.file_reader = file_reader
        self.read_fs = read_fs
        self.write_fs = write_fs
        self.listing_file_system = listing_file_system
        self.version = version
        self.volumes = volumes
        self.top_trash_dir_rules_reader = \
            top_trash_dir_rules_reader or RealTopTrashDirFs()

    no_args = object()

    def run_restore(self, args=no_args, reply='', from_dir=None):
        args = [] if args is self.no_args else args
        stdout = StringIO()
        stderr = StringIO()
        read_cwd = FakeReadCwd(from_dir)
        logger = MemoLogger()
        cmd = RestoreCmd.make_from_environment(
            stdout=stdout,
            stderr=stderr,
            exit=sys.exit,
            input=HardCodedInput(reply),
            version=self.version,
            listing_file_system=self.listing_file_system,
            volumes=self.volumes,
            logger=logger,
            uid=self.uid,
            environ=self.environ,
            top_trash_dir_rules_fs=self.top_trash_dir_rules_reader,
            file_reader=self.file_reader,
            read_fs=self.read_fs,
            write_fs=self.write_fs,
            read_cwd=read_cwd)

        try:
            exit_code = cmd.run(args)
        except SystemExit as e:
            exit_code = e.code

        return CmdResult(stdout.getvalue(),
                         stderr.getvalue(), exit_code)
