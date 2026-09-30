import sys
from io import StringIO
from typing import Dict, Optional

from tests.support.run.cmd_result import CmdResult
from tests.test_restore.support.fake_read_cwd import FakeReadCwdFs
from tests.test_restore.support.recording_logger import RecordingLogger
from trashcli.fslib.protocols.list_files_in_dir import ListFilesInDir
from trashcli.fstab.volumes import Volumes
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.fs.volume_path_fs import VolumePathFs
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.fs.protocols.file_reader_fs import FileReaderFs
from trashcli.restore.fs.protocols.restore_writer_fs import RestoreWriterFs
from trashcli.restore.fs.protocols.restore_read_fs import RestoreReadFs
from trashcli.restore.restore_logger import RestoreLogger
from trashcli.trash_dirs_scanner import TopTrashDirRulesFs


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
                 volume_path_fs,  # type: VolumePathFs
                 logger,  # type: RestoreLogger
                 top_trash_dir_rules_reader,  # type: TopTrashDirRulesFs
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
        self.volume_path_fs = volume_path_fs
        self.top_trash_dir_rules_reader = top_trash_dir_rules_reader
        self.logger = logger

    no_args = object()

    def run_restore(self, args=no_args, reply='', from_dir=None):
        args = [] if args is self.no_args else args
        stdout = StringIO()
        stderr = StringIO()
        read_cwd = FakeReadCwdFs(from_dir)
        cmd = RestoreCmd(
            stdout=stdout,
            stderr=stderr,
            exit=sys.exit,
            input=HardCodedInput(reply),
            version=self.version,
            listing_fs=self.listing_fs,
            volumes=self.volumes,
            logger=self.logger,
            uid=self.uid,
            environ=self.environ,
            top_trash_dir_rules_fs=self.top_trash_dir_rules_reader,
            file_reader=self.file_reader,
            read_fs=self.path_read_fs,
            write_fs=self.write_fs,
            read_cwd=read_cwd,
            volume_path_fs=self.volume_path_fs)

        try:
            exit_code = cmd.run(args)
        except SystemExit as e:
            exit_code = e.code

        return CmdResult(stdout.getvalue(),
                         stderr.getvalue(), exit_code)
