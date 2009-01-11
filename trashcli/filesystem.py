from __future__ import absolute_import

import os
import shutil
from ctypes import *
from ctypes.util import find_library
import sys 
import unipath

class Path (unipath.Path) :
    sep = '/'
    def __init__(self, path) :
        assert(isinstance(path,str))
        self.path = os.path.normpath(path).replace(os.path.sep, self.sep)
        if self.path.lower().startswith("c:") :
            self.path = self.path [len("c:"):]

    # TODO: use "@property"
    def __get_parent(self) :
        return Path(os.path.dirname(self.path))
    parent = property(__get_parent)

    @property
    def realpath(self) :
        return Path(os.path.realpath(self.path))

    @property
    def basename(self) :
        return os.path.basename(self.path)

    def move(self, dest) :
        return shutil.move(self.path, str(dest))

    def __join_str(self, path) :
        return Path(os.path.join(self.path, path))

    def __join_Path(self, path) :
        assert(isinstance(path, Path))
        if path.isabs() :
            raise ValueError("File with relative path expected")
        return self.__join_str(path.path)

    def join(self, path) :
        if(isinstance(path,Path)):
            return self.__join_Path(path)
        elif(isinstance(path,str)):
            return self.__join_str(path)
        else :
            raise TypeError("Expected argument type as 'File' or 'str'")

    """
    return Volume the volume where the file is
    """
    @property
    def volume(self) :
        return Volume.volume_of(self.path)

    def remove(self) :
        if(self.exists()):
            try:
                os.remove(self.path)        
            except:
                return shutil.rmtree(self.path)

    def exists(self) :
        return os.path.exists(self.path)

    def isdir(self) :
        return os.path.isdir(self.path)

    def islink(self) :
        return os.path.islink(self.path)

    def has_sticky_bit(self):
        import os
        import stat
        return (os.stat(self.path).st_mode & stat.S_ISVTX) == stat.S_ISVTX
    
    def isabs(self) :
        return os.path.isabs(self.path)

    def __eq__(self, other) :
        if self is other:
            return True
        if self.path == other:
            return True
        return False

    def __str__(self) :
        return str(self.path)

    def list(self) :
        for filename in os.listdir(self.path) :
            yield self.join(filename)

    def mkdir(self):
        os.mkdir(self.path)

    def mkdirs(self, mode=0777):
        if self.isdir():
            os.chmod(self.path, mode)
            return 
        os.makedirs(self.path, mode)

    def touch(self):
        open(self.path, "w").close()
    
    def read(self):
        f=self.open()
        result=f.read()
        f.close()
        return result

    def open(self):
        return open(self.path)
    
    def ismount(self):
        return os.path.ismount(self.path)
    
    def __repr__(self):
        return "Path('%s')" % self.path

class Volume(object) :
    def __init__(self,path, permissive = False):
        assert(isinstance(path,Path))
        if True or permissive or os.path.ismount(path.path) :
            self.path=path 
        else:
            raise ValueError("path is not a mount point:" + path)

    @property
    def topdir(self) :
        assert(isinstance(self.path, Path))
        return self.path

    def __cmp__(self, other) :
        if not isinstance(other, self.__class__) :
            return False
        else :
            return cmp(self.path,other.path)

    def __str__(self) :
        return str(self.path)

    # TODO: move to trash.py module
    def hasCommonTrashDirectory(self) :
        """
        checks required by trash specification
        (from http://www.ramendik.ru/docs/trashspec.0.7.html)

         1. check if $topdir/.Trash exist
         2. check if $topdir/.Trash is a directory
         3. check if $topdir/.Trash is not a symbolic link
         4. check it $topdir/.Trash has sticky bit
        """
        trashdir = self.path.join(".Trash")
        return trashdir.exists() and trashdir.isdir() and not trashdir.islink()

    @staticmethod
    def volume_of(path) : 
        path = os.path.realpath(path)
        while path != os.path.dirname(path):
            if os.path.ismount(path):
                break
            path = os.path.dirname(path)
        return Volume(Path(path))

    @staticmethod
    def mounted_filesystems() :
        class Filesystem:
            def __init__(self, mount_dir, type, name) :
                self.mount_dir = mount_dir
                self.type = type
                self.name = name
        class mntent_struct(Structure):
            _fields_ = [("mnt_fsname", c_char_p),  # Device or server for filesystem.
                        ("mnt_dir", c_char_p),     # Directory mounted on.
                        ("mnt_type", c_char_p),    # Type of filesystem: ufs, nfs, etc.
                        ("mnt_opts", c_char_p),    # Comma-separated options for fs.
                        ("mnt_freq", c_int),       # Dump frequency (in days).
                        ("mnt_passno", c_int)]     # Pass number for `fsck'.

        if sys.platform == "cygwin":
            libc_name = "cygwin1.dll"
        else:
            libc_name = find_library("c")

        if libc_name == None :
            libc_name="/lib/libc.so.6" # fix for my Gentoo 4.0

        libc = cdll.LoadLibrary(libc_name)
        libc.getmntent.restype = POINTER(mntent_struct)
        libc.fopen.restype = c_void_p

        f = libc.fopen("/proc/mounts", "r")
        if f==None:
            f = libc.fopen("/etc/mtab", "r")
            if f == None:
                raise IOError("Unable to open /proc/mounts nor /etc/mtab")

        while True:
            entry = libc.getmntent(f)
            if bool(entry) == False: 
                libc.fclose(f)
                break
            yield Filesystem(entry.contents.mnt_dir,
                             entry.contents.mnt_type,
                             entry.contents.mnt_fsname)

    def __repr__(self):
        return "[Path:%s]" % self.path
    
    @staticmethod
    def all() :
        return [ Volume(Path(elem.mount_dir)) for elem in Volume.mounted_filesystems()]