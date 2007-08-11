#!/usr/bin/python

import libtrash.trash_directory
import os

td = libtrash.trash_directory.getHomeTrashDirectory()
list = td.getTrashedFileInDir(os.curdir)
for i in range(0,len(list)) :
    trashedfile = list[i]
    print "%4d %s %s" % (i, trashedfile.getDeletionTime(), trashedfile.getPath())


index=raw_input("What file to restore [0..%d]: " % (len(list)-1))
if index == "" :
    print "Exiting"
else :
    index = int(index)
    list[index].restore()
