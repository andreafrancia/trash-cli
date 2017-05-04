# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

import sys,os

def restore():
    from trashcli.restore import RestoreCmd
    try:           # Python 2
        input23 = raw_input
    except:        # Python 3
        input23 = input
    RestoreCmd(
        stdout  = sys.stdout,
        stderr  = sys.stderr,
        environ = os.environ,
        exit    = sys.exit,
        input   = input23
    ).run(sys.argv)

def empty(argv    = sys.argv,
          stdout  = sys.stdout,
          stderr  = sys.stderr,
          environ = os.environ):
    from trashcli.empty import EmptyCmd
    from trashcli.list_mount_points import mount_points
    from datetime import datetime
    from trashcli.trash import FileSystemReader
    from trashcli.fs import FileRemover
    from trashcli.trash import version
    return EmptyCmd(
        out          = stdout,
        err          = stderr,
        environ      = environ,
        list_volumes = mount_points,
        now          = datetime.now,
        file_reader  = FileSystemReader(),
        getuid       = os.getuid,
        file_remover = FileRemover(),
        version      = version,
    ).run(*argv)


def list():
    from trashcli.list import ListCmd
    from trashcli.list_mount_points import mount_points
    ListCmd(
        out          = sys.stdout,
        err          = sys.stderr,
        environ      = os.environ,
        getuid       = os.getuid,
        list_volumes = mount_points,
    ).run(*sys.argv)

