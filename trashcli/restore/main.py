# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from .real_restore_logger import RealRestoreLogger
from .restore_cmd import RestoreCmd
from ..fs_impl import RealReasCwd
from ..fstab.volumes import RealVolumes
from ..lib.environ import cast_environ
from ..lib.logger import my_logger
from ..lib.my_input import RealInput
from ..put.fs.real_fs import RealFs


def main():
    RestoreCmd.make(
        stdout=sys.stdout,
        stderr=sys.stderr,
        exit=sys.exit,
        user_input=RealInput(),
        version=trashcli.trash.version,
        volumes=RealVolumes(),
        uid=os.getuid(),
        environ=cast_environ(os.environ),
        logger=RealRestoreLogger(my_logger),
        read_cwd=RealReasCwd(),
        fs=RealFs(),
    ).run(sys.argv)
