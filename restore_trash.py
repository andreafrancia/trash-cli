# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import RestoreCmd
import sys, os

def main():
    RestoreCmd(
        stdout  = sys.stdout,
        stderr  = sys.stderr,
        environ = os.environ,
        exit    = sys.exit,
        input   = raw_input
    ).run()

if __name__ == '__main__':
    main()
