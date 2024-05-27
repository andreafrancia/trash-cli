import sys
from typing import List
from typing import Optional

from six import StringIO
from six import text_type

from tests.support.restore.fs.fake_read_cwd import FakeReadCwd
from tests.support.restore.logger.fake_logger import FakeLogger
from tests.support.run.cmd_result import CmdResult
from trashcli.fstab.volumes import Volumes
from trashcli.lib.environ import Environ
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.fs.fs import Fs
from trashcli.restore.restore_cmd import RestoreCmd


class RestoreUser:
    def __init__(self,
                 environ,  # type: Environ
                 uid,  # type: int
                 version,  # type: str
                 volumes,  # type: Volumes
                 restore_fs,  # type: Fs
                 fs,  # type: Fs
                 cwd=None,  # type: Optional[text_type]
                 reply=None,  # type: Optional[text_type]
                 ):
        self.environ = environ
        self.uid = uid
        self.restore_fs = restore_fs
        self.fs = fs
        self.version = version
        self.volumes = volumes
        self.cwd = cwd
        self.reply = reply

    def run_restore(self,
                    args=None,  # type: Optional[List[str]]
                    reply=None,  # type: Optional[text_type]
                    from_dir=None):
        args = [] if args is None else args
        cwd = self.cwd if from_dir is None else from_dir
        reply = self.reply if reply is None else reply
        stdout = StringIO()
        stderr = StringIO()
        logger = FakeLogger(stderr)

        cmd = RestoreCmd.make(
            stdout=stdout,
            stderr=stderr,
            exit=sys.exit,
            user_input=HardCodedInput(reply),
            version=self.version,
            volumes=self.volumes,
            uid=self.uid,
            environ=self.environ,
            logger=logger,
            read_cwd=FakeReadCwd(cwd),
            fs=self.restore_fs
        )
        return CmdResult.run_cmd(lambda: cmd.run(args), stdout, stderr)
