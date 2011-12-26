# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

import sys
from trashcli.trash import TrashPutCmd

def main():
    TrashPutCmd(
        sys.stdout,
        sys.stderr
    ).run(sys.argv)

if __name__ == '__main__':
    main()
