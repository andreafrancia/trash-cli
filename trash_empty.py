# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

import sys
import os

from trashcli.trash import EmptyCmd

def main():
    EmptyCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
    ).run(*sys.argv)

if __name__ == '__main__':
    main()
