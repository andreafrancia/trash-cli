# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_volumes import RealVolumesFs
from trashcli.lib.logger import my_logger
from trashcli.lib.my_input import RealInput
from trashcli.restore.fs.real.real_restore_fs import RealRestoreFs
from trashcli.restore.real_restore_logger import RealRestoreLogger
from trashcli.restore.restore_cmd import RestoreCmd


def main():
    RestoreCmd(
        stdout=sys.stdout,
        stderr=sys.stderr,
        exit=sys.exit,
        input=RealInput(),
        version=trashcli.trash.version,
        listing_fs=RealRestoreFs(),
        volumes=RealVolumesFs(),
        logger=RealRestoreLogger(my_logger),
        uid=os.getuid(),
        environ=os.environ,
        top_trash_dir_rules_fs=RealFs(),
        file_reader=RealRestoreFs(),
        read_fs=RealRestoreFs(),
        write_fs=RealRestoreFs(),
        read_cwd=RealRestoreFs(),
    ).run(sys.argv)
