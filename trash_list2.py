# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

import sys, os
from trashcli.trash2 import ListCmd

def main():
    ListCmd(
        out     = sys.stdout,
        err     = sys.stderr,
        environ = os.environ,
        getuid  = os.getuid
    ).run(*sys.argv)

if __name__ == '__main__':
    main()
