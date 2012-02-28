# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

import sys,os

def put():
    from trashcli.trash import TrashPutCmd
    TrashPutCmd(
        sys.stdout,
        sys.stderr
    ).run(sys.argv)


def restore():
    from trashcli.trash import RestoreCmd
    RestoreCmd(
        stdout  = sys.stdout,
        stderr  = sys.stderr,
        environ = os.environ,
        exit    = sys.exit,
        input   = raw_input
    ).run()

def empty():
    from trashcli.trash import EmptyCmd
    EmptyCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
    ).run(*sys.argv)


def list():
    from trashcli.trash import ListCmd
    ListCmd(
        out     = sys.stdout,
        err     = sys.stderr,
        environ = os.environ,
        getuid  = os.getuid
    ).run(*sys.argv)
