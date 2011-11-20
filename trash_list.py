#!/usr/bin/python
# Copyright (C) 2007-2009 Andrea Francia Trivolzio(PV) Italy

import sys
from trashcli.trash import List

def main():
    List(sys.stdout).main(*sys.argv)

if __name__ == '__main__':
    main()
