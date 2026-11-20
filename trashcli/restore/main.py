# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from trashcli.fslib.real.real_fs import RealFs
from trashcli.lib.logger import my_logger
from trashcli.lib.my_input import RealInput
from trashcli.restore.real_restore_logger import RealRestoreLogger
from trashcli.restore.restore_cmd import RestoreCmd


def main():
    fs = RealFs()
    RestoreCmd(
        stdout=sys.stdout,
        stderr=sys.stderr,
        exit=sys.exit,
        input=RealInput(),
        version=trashcli.trash.version,
        listing_fs=fs,
        volumes=fs,
        logger=RealRestoreLogger(my_logger),
        uid=os.getuid(),
        environ=os.environ,
        top_trash_dir_rules_fs=fs,
        file_reader=fs,
        read_fs=fs,
        write_fs=fs,
        read_cwd=fs,
    ).run(sys.argv)
