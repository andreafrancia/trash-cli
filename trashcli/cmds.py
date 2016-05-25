# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

import sys,os

def restore():
    from trashcli.trash import RestoreCmd
# Try Python 2 raw_input function; if NameError occurs, use Python 3 input function
    try:
        RestoreCmd(
            stdout  = sys.stdout,
            stderr  = sys.stderr,
            environ = os.environ,
            exit    = sys.exit,
            input   = raw_input
        ).run(sys.argv)
    except NameError:
        RestoreCmd(
            stdout  = sys.stdout,
            stderr  = sys.stderr,
            environ = os.environ,
            exit    = sys.exit,
            input   = input
        ).run(sys.argv)


def empty():
    from trashcli.trash import EmptyCmd
    from trashcli.list_mount_points import mount_points
    return EmptyCmd(
        out          = sys.stdout,
        err          = sys.stderr,
        environ      = os.environ,
        list_volumes = mount_points,
    ).run(*sys.argv)


def list():
    from trashcli.trash import ListCmd
    from trashcli.list_mount_points import mount_points
    ListCmd(
        out          = sys.stdout,
        err          = sys.stderr,
        environ      = os.environ,
        getuid       = os.getuid,
        list_volumes = mount_points,
    ).run(*sys.argv)

