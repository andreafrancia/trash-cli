import sys
from io import StringIO
from typing import Dict, Optional

from tests.support.run.cmd_result import CmdResult
from tests.test_restore.support.fake_read_cwd import FakeReadCwdFs
from trashcli.fslib.protocols.volumes_fs import VolumesFs
from trashcli.lib.environ import Environ
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.fs.protocols.restore_fs import RestoreFs
from trashcli.restore.restore_logger import RestoreLogger


class RestoreUser:
    def __init__(self,
                 environ,  # type: Environ
                 uid,  # type: int
                 fs,  # type: RestoreFs
                 version,  # type: str
                 volumes,  # type: VolumesFs
                 logger,  # type: RestoreLogger
                 ):
        self.fs = fs
        self.environ = environ
        self.uid = uid
        self.version = version
        self.volumes = volumes
        self.logger = logger

    no_args = object()

    def run_restore(self,
                    args=no_args,
                    reply='',  # type: str
                    from_dir=None,  # type: Optional[str]
                    ):
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
            fs=self.fs,
            volumes=self.volumes,
            logger=self.logger,
            uid=self.uid,
            environ=self.environ,
            read_cwd=read_cwd,
        )

        try:
            exit_code = cmd.run(args)
        except SystemExit as e:
            exit_code = e.code

        return CmdResult(stdout.getvalue(),
                         stderr.getvalue(), exit_code)
