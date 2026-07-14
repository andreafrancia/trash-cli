import sys
from io import StringIO
from typing import Dict, Optional

from tests.support.run.cmd_result import CmdResult
from tests.test_restore.support.fake_read_cwd import FakeReadCwdFs
from tests.test_restore.support.memo_logger import MemoLogger
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fslib.fs_operations import ListFilesInDir
from trashcli.fstab.volumes import Volumes
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.restore_fs import FileReaderFs, RestoreWriterFs, \
    RestoreReadFs


class RestoreUser:
    def __init__(self,
                 environ,  # type: Dict[str, str]
                 uid,  # type: int
                 file_reader,  # type: FileReaderFs
                 path_read_fs,  # type: RestoreReadFs
                 write_fs,  # type: RestoreWriterFs
                 listing_fs,  # type: ListFilesInDir
                 version,  # type: str
                 volumes,  # type: Volumes
                 top_trash_dir_rules_reader=None,
                 read_fs=None,  # type: Optional[RestoreReadFs]
                 ):
        self.environ = environ
        self.uid = uid
        self.file_reader = file_reader
        self.path_read_fs = path_read_fs
        self.write_fs = write_fs
        self.listing_fs = listing_fs
        self.version = version
        self.volumes = volumes
        self.top_trash_dir_rules_reader = \
            top_trash_dir_rules_reader or RealTopTrashDirFs()

    no_args = object()

    def run_restore(self, args=no_args, reply='', from_dir=None):
        args = [] if args is self.no_args else args
        stdout = StringIO()
        stderr = StringIO()
        read_cwd = FakeReadCwdFs(from_dir)
        logger = MemoLogger()
        cmd = RestoreCmd(
            stdout=stdout,
            stderr=stderr,
            exit=sys.exit,
            input=HardCodedInput(reply),
            version=self.version,
            listing_fs=self.listing_fs,
            volumes=self.volumes,
            logger=logger,
            uid=self.uid,
            environ=self.environ,
            top_trash_dir_rules_fs=self.top_trash_dir_rules_reader,
            file_reader=self.file_reader,
            read_fs=self.path_read_fs,
            write_fs=self.write_fs,
            read_cwd=read_cwd)

        try:
            exit_code = cmd.run(args)
        except SystemExit as e:
            exit_code = e.code

        return CmdResult(stdout.getvalue(),
                         stderr.getvalue(), exit_code)
