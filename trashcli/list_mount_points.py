# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy

def mount_points():
    try:
	return list(mount_points_from_getmnt())
    except AttributeError:
        return mount_points_from_df()

def mount_points_from_getmnt():
    for elem in _mounted_filesystems_from_getmnt():
        yield elem.mount_dir

def mount_points_from_df():
    import subprocess
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
    from ctypes import (
        c_char_p, c_int, c_void_p, cdll, POINTER, pythonapi, Structure, util)
    import sys
    class Filesystem:
        def __init__(self, mount_dir, type, name) :
            self.mount_dir = mount_dir
            self.type = type
            self.name = name
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
        libc_name = util.find_library("c") or "/lib/libc.so.6" # fix for my Gentoo 4.0
    libc = cdll.LoadLibrary(libc_name)
    libc.getmntent.restype = POINTER(mntent_struct)
    PyFile_AsFile = pythonapi.PyFile_AsFile
    PyFile_AsFile.argtypes = [pythonapi.py_object]

    try:
        f = open("/proc/mounts")
    except IOError:
        try:
            f = open("/etc/mtab")
        except IOError:
            raise IOError("Unable to open /proc/mounts nor /etc/mtab")

    for entry in iter(lambda: libc.getmntent(PyFile_AsFile(f)), None):
        yield Filesystem(entry.contents.mnt_dir,
                         entry.contents.mnt_type,
                         entry.contents.mnt_fsname)

    f.close()
