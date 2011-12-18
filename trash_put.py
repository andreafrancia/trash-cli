# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import TrashPutCmd

def main():
    import sys
    cmd=TrashPutCmd(sys.stdout,sys.stderr)
    cmd.run(sys.argv)

if __name__ == '__main__':
    main()
