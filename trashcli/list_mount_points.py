# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy
from collections import namedtuple
from ctypes import Structure, c_char_p, c_int, c_void_p, cdll, POINTER
from ctypes.util import find_library
from itertools import imap, repeat, takewhile
import subprocess
import sys


def mount_points():
    try:
	return list(mount_points_from_getmnt())
    except AttributeError:
        return mount_points_from_df()


def mount_points_from_getmnt():
    for elem in _mounted_filesystems_from_getmnt():
        yield elem.mount_dir


def mount_points_from_df():
    df_output = subprocess.Popen(["df", "-P"], stdout=subprocess.PIPE).stdout
    return list(_mount_points_from_df_output(df_output))


def _mount_points_from_df_output(df_output):
    def skip_header():
	df_output.readline()
    def chomp(string):
	return string.rstrip('\n')

    skip_header()
    for line in df_output:
	line = chomp(line)
	yield line.split(None, 5)[-1]


def _mounted_filesystems_from_getmnt() :

    Filesystem = namedtuple("Filesystem", "mount_dir type name")

    class mntent_struct(Structure):
        _fields_ = [("mnt_fsname", c_char_p),  # Device or server for
                                               # filesystem.
                    ("mnt_dir", c_char_p),     # Directory mounted on.
                    ("mnt_type", c_char_p),    # Type of filesystem: ufs,
                                               # nfs, etc.
                    ("mnt_opts", c_char_p),    # Comma-separated options
                                               # for fs.
                    ("mnt_freq", c_int),       # Dump frequency (in days).
                    ("mnt_passno", c_int)]     # Pass number for `fsck'.

    if sys.platform == "cygwin":
        libc_name = "cygwin1.dll"
    else:
        libc_name = (find_library("c") or
                     find_library("/lib/libc.so.6")) # fix for Gentoo 4.0

    libc = cdll.LoadLibrary(libc_name)
    libc.fopen.restype = c_void_p
    libc.getmntent.argtypes = libc.fclose.argtypes = [c_void_p]
    libc.getmntent.restype = POINTER(mntent_struct)

    f = libc.fopen("/proc/mounts", "r") or libc.fopen("/etc/mtab", "r")
    if not f:
        raise IOError("Unable to open /proc/mounts nor /etc/mtab")

    for entry in takewhile(bool, imap(libc.getmntent, repeat(f))):
        yield Filesystem(entry.contents.mnt_dir,
                         entry.contents.mnt_type,
                         entry.contents.mnt_fsname)

    libc.fclose(f)
