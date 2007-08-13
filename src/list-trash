#!/usr/bin/python

import libtrash.trash_directory

def printTrashedFile(trashedfile) :
    print "%s %s" % (trashedfile.getDeletionTime(), trashedfile.getPath())

td = libtrash.trash_directory.getHomeTrashDirectory()
td.forEachTrashedFile(printTrashedFile)