import StringIO
import exceptions
import os
import re
import shutil
import string
import sys
import time
import urllib
import random
from datetime import datetime
from stat import *
import traceback
import logging
from ctypes import *
from ctypes.util import find_library

#logging.root.setLevel(0)

# the distribution script will change this to actual version number
version='svn'

class File (object) :
    sep = '/'
    def __init__(self, path) :
        self.path = os.path.normpath(path).replace(os.path.sep, self.sep)
        if self.path .startswith("C:") :
            self.path = self.path [len("C:"):]

    def getParent(self) :
        return File(os.path.dirname(self.path))
    parent = property(getParent)

    @property
    def realpath(self) :
        return File(os.path.realpath(self.path))

    @property
    def basename(self) :
        return os.path.basename(self.path)

    def move(self, dest) :
        return shutil.move(self.path, dest)

    def join(self, path) :
        return File(os.path.join(self.path, path))

    def samefs(path1, path2):
        if not (os.path.exists(path1) and os.path.exists(path2)):
            return False

        while path1 != os.path.dirname(path1):
            if os.path.ismount(path1):
                break
            path1 = os.path.dirname(path1)

        while path2 != os.path.dirname(path2):
            if os.path.ismount(path2):
                break
            path2 = os.path.dirname(path2)

        return path1 == path2  

    """
    return Volume the volume where the file is
    """
    @property
    def volume(self) :
        return Volume.volumeOf(self.path)

    # TODO: remove
    def getPath(self) :
        return self.path

    def remove(self) :
        try:
            os.remove(self.path)        
        except:
            return shutil.rmtree(self.path, True)

    def exists(self) :
        return os.path.exists(self.getPath())

    def isdir(self) :
        return os.path.isdir(self.getPath())

    def islink(self) :
        return os.path.islink(self.getPath())

    def __cmp__(self, other) :
        if not isinstance(other, self.__class__) :
            return False
        else :
            return cmp(self.path,other.path)

    def __str__(self) :
        return str(self.path)

"""
Represent a trash directory.
For example $XDG_DATA_HOME/Trash
"""
class TrashDirectory(object) :
    def __init__(self, path, volume) :
        assert isinstance(path,File)
        assert isinstance(volume,File)
        self.path = path
        self.volume = volume

    def __str__(self) :
        return str(self.path)

    """ 
    Trash the specified file.
    returns TrashedFile
    """
    def trash(self, fileToBeTrashed):
        assert(isinstance(fileToBeTrashed, File))
        if not self.volume == fileToBeTrashed.parent.volume :
            raise "file is not in the same volume of trash directory!"

        trashInfo = self.createTrashInfo(fileToBeTrashed, datetime.now())

        if not os.path.exists(self.getFilesPath()) : 
            os.makedirs(self.getFilesPath(), 0700)

        try :
            fileToBeTrashed.move(self.getOriginalCopyPath(trashInfo.getId()))
        except IOError, e :
            self.getTrashInfoFile(trashInfo.getId()).remove();
            raise e

        return TrashedFile(trashInfo, self)

    def getBasePath(self) :
        return self.volume.getPath()

    def getInfoPath(self) :
        return os.path.join(self.path.path, "info")

    def getFilesPath(self) :
        return os.path.join(self.path.path, "files")

    def trashedFiles(self) :
        try : 
            for filename in os.listdir(self.getInfoPath()) :
                infoFilename = os.path.join(self.getInfoPath(), filename)

                infoBasename = os.path.basename(infoFilename)

                if not infoBasename.endswith('.trashinfo') :
                    raise AssertionError()

                ti = TrashInfo.parse(open(infoFilename).read())
                yield TrashedFile(ti, self)
        except OSError, e: # when directory does not exist
            pass 

    def trashedFilesInDir(self, dir) :
        dir = os.path.realpath(dir)
        for trashedfile in self.trashedFiles() :
            if trashedfile.getPath().startswith(dir + File.sep) :
                yield trashedfile

    def getOriginalCopyPath(self, trashId) :
        return self.getOriginalCopy(trashId).getPath()

    def getOriginalCopy(self, trashId) :
        return File(os.path.join(self.getFilesPath(), str(trashId)))

    def getTrashInfoFile(self, trashId) :
        return File(os.path.join(self.getInfoPath(), str(trashId) + '.trashinfo'))

    def removeInfoFile(self, trashId) :
        self.getTrashInfoFile(trashId).remove()

    def _path_for_trashinfo(self, fileToTrash):
        raise NotImplementedError


    """
    Create a .trashinfo file in the $trash/info directory.
    param File fileToBeTrashed
    param ? deletionTime
    returns TrashInfo the create TrashInfo file.
    """
    def createTrashInfo(self, fileToBeTrashed, deletion_date) :
        assert(isinstance(fileToBeTrashed, File))

        # create trash info
        trashInfo = TrashInfo(self._path_for_trashinfo(fileToBeTrashed),deletion_date)


        # write trash info
        index = 0
        while True :
            if index == 0 :
                suffix = ""
            elif index < 100:
                suffix = "_%d" % index
            else :
                suffix = "_%d" % random.randint(0, 65535)

            base_id = fileToBeTrashed.basename
            trash_id = base_id + suffix
            trashInfoBasename = trash_id + ".trashinfo"

            if not os.path.exists(self.getInfoPath()) : 
                try :
                    os.makedirs(self.getInfoPath(), 0700)
                except OSError:
                    logging.debug(traceback.print_exc())
                    try: 
                        os.makedirs(self.getInfoPath())
                    except:
                        logging.debug(traceback.print_exc())


            dest = os.path.join(self.getInfoPath(),trashInfoBasename)
            try :
                handle = os.open(dest, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0600)
                os.write(handle, trashInfo.render())
                os.close(handle)
                logging.debug(".trashinfo created as %s." % dest)
                trashInfo.setId(trash_id)
                return trashInfo
            except OSError, e:
                logging.debug("Attempt for creating %s failed." % dest)

            index += 1

        raise IOError()

    # staticmethod
    def getHomeTrashDirectory() : 
        if 'XDG_DATA_HOME' in os.environ:
            XDG_DATA_HOME = os.environ['XDG_DATA_HOME']
        else :
            XDG_DATA_HOME = os.environ['HOME'] + '/.local/share'

        path = File(XDG_DATA_HOME + "/Trash")
        return HomeTrashDirectory(path)
    getHomeTrashDirectory=staticmethod(getHomeTrashDirectory)

    # staticmethod
    def allTrashedFiles() :
        for trashedfile in TrashDirectory.getHomeTrashDirectory().trashedFiles() :
            yield trashedfile

        for volume in Volume.all() :
            for trashedfile in volume.getCommonTrashDirectory().trashedFiles() :
                yield trashedfile    
            for trashedfile in volume.getUserTrashDirectory().trashedFiles() :
                yield trashedfile
    allTrashedFiles=staticmethod(allTrashedFiles)

    # classmethod
    def allTrashedFilesInDir(cls,dir) :
        dir = os.path.realpath(dir)
        for trashedfile in cls.allTrashedFiles() :
            if trashedfile.getPath().startswith(dir + os.path.sep) :
                yield trashedfile
    allTrashedFilesInDir=classmethod(allTrashedFilesInDir)    

class HomeTrashDirectory(TrashDirectory) :
    def __init__(self, path) :
        assert isinstance(path, File)

        TrashDirectory.__init__(self, path, path.volume)

    def _path_for_trashinfo(self, fileToBeTrashed) :
        assert isinstance(fileToBeTrashed, File)

        # for the HomeTrashDirectory all path are stored as absolute

        parent = fileToBeTrashed.realpath.parent
        return parent.join(fileToBeTrashed.basename)

class VolumeTrashDirectory(TrashDirectory) :
    def __init__(self, path, volume) :
        assert isinstance(path, File)
        assert isinstance(volume, File)
        TrashDirectory.__init__(self,path, volume)

    def _path_for_trashinfo(self, fileToBeTrashed) :
        # for the VolumeTrashDirectory paths are stored as relative 
        # if possible

        # string representing the parent of the fileToBeTrashed
        parent=fileToBeTrashed.parent.realpath
        topdir=self.volume.getPath()   # e.g. /mnt/disk-1

        if parent.path.startswith(topdir+File.sep) :
            parent = File(parent.path[len(topdir+File.sep):])

        return parent.join(fileToBeTrashed.basename)                      


class TrashedFile (object) :
    def __init__(self,trashinfo,trashdirectory) :
        assert isinstance(trashinfo, TrashInfo)
        assert isinstance(trashdirectory, TrashDirectory)
        self.__trashinfo = trashinfo
        self.__trashdirectory = trashdirectory

    def getPath(self) :
        return os.path.join(self.__trashdirectory.getBasePath(), self.__trashinfo.getPath().path)

    def getDeletionTime(self) :
        return self.__trashinfo.getDeletionTime()

    def restore(self) :
        if not os.path.exists(os.path.dirname(self.getPath())) :
            os.makedirs(os.path.dirname(self.getPath()))

        trashId = self.__trashinfo.getId()
        self.__trashdirectory.getOriginalCopy(trashId).move(self.getPath())
        self.__trashdirectory.getTrashInfoFile(trashId).remove()

    def purge(self) :
        # author : Einar Orn Olason
        trashId = self.__trashinfo.getId()
        self.__trashdirectory.getOriginalCopy(trashId).remove()
        self.__trashdirectory.getTrashInfoFile(trashId).remove()

    @property
    def trash_directory(self) :
        return self.__trashdirectory


class TrashInfo (object) :
    def __init__(self, path, deletion_date, trashId = None) :
        assert isinstance(path, File)
        assert isinstance(deletion_date, datetime)
        assert trashId == None or isinstance(trashId, str)
        self.__id = trashId
        self.__path = path
        self.__deletion_date = deletion_date

    def setDeletionTime(self, value) :
        self.__deletion_date  = value

    def setPath(self, path) :
        assert isinstance(path, File)
        self.__path = path

    def getDeletionTimeAsString(self) :
        return datetime.strftime(self.__deletion_date, "%Y-%m-%dT%H:%M:%S")

    def getDeletionTime(self) :
        return self.__deletion_date

    def getPath(self) :
        return self.__path

    def getId(self) :
        return self.__id

    def setId(self, trashId) :
        self.__id = trashId

    @staticmethod
    def parse(data) :
        path = None
        deletion_date = None

        stream = StringIO.StringIO(data)
        line = stream.readline().rstrip('\n')
        if line != "[Trash Info]" :
            raise ValueError()

        try :
            line = stream.readline().rstrip('\n')
        except :
            raise ValueError()

        match = re.match("^Path=(.*)$", line)
        if match == None :
            raise ValueError()
        try :
            path = File(urllib.unquote(match.groups()[0]))
        except IndexError, e:
            raise ValueError()


        try :
            line = stream.readline().rstrip('\n')
        except :
            raise ValueError()

        match = re.match("^DeletionDate=(.*)$", line)
        if match == None :
            raise ValueError()
        try :
            deletion_date_string=match.groups()[0] # as string
            deletion_date=TimeUtils.parse_iso8601(deletion_date_string)
        except IndexError, e:
            raise ValueError()

        return TrashInfo(path, deletion_date)

    def render(self) :
        result = "[Trash Info]\n"
        result += "Path=" + urllib.quote(self.getPath().path,'/') + "\n"
        result += "DeletionDate=" + self.getDeletionTimeAsString() + "\n"
        return result

class TimeUtils(object):
    def parse_iso8601(text) :
        t=time.strptime(text,  "%Y-%m-%dT%H:%M:%S")
        return datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    parse_iso8601=staticmethod(parse_iso8601)

class Volume (File) :
    def __init__(self,path, permissive = False):
        if True or permissive or os.path.ismount(path) :
            File.__init__(self,path)
        else:
            raise ValueError("path is not a mount point:" + path)
        try:
            self.getuid = os.getuid
        except AttributeError:
            self.getuid = lambda: 0

    def sameVolume(self,path) : 
        return Volume.volumeOf(path).path == self.path

    # TODO: replace with @property path
    def getPath(self) :
        return self.path

    def __cmp__(self, other) :
        if not isinstance(other, self.__class__) :
            return False
        else :
            return cmp(self.path,other.path)

    def __str__(self) :
        return str(self.path)

    def hasCommonTrashDirectory(self) :
        """
        checks required by trash specification
        (from http://www.ramendik.ru/docs/trashspec.0.7.html)

         1. check if $topdir/.Trash exist
         2. check if $topdir/.Trash is a directory
         3. check if $topdir/.Trash is not a symbolic link
         4. check it $topdir/.Trash has sticky bit
        """
        trashdir = self.join(".Trash")
        return trashdir.exists() and trashdir.isdir() and not trashdir.islink()

    def getCommonTrashDirectory(self) :
        uid = self.getuid()
        trash_directory_path = File(os.path.join(self.getPath(), ".Trash", str(uid)))

        return VolumeTrashDirectory(trash_directory_path,self)

    def getUserTrashDirectory(self) :
        uid = self.getuid()
        trash_directory_path = File(os.path.join(self.getPath(), ".Trash-%s" % str(uid)))

        return VolumeTrashDirectory(trash_directory_path,self)

    # staticmethod
    def volumeOf(path) : 
        path = os.path.realpath(path)
        while path != os.path.dirname(path):
            if os.path.ismount(path):
                break
            path = os.path.dirname(path)
        return Volume(path)
    volumeOf=staticmethod(volumeOf)

    # staticmethod
    def __mounted_filesystems() :
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

            libc = cdll.LoadLibrary(libc_name)
        libc.getmntent.restype = POINTER(mntent_struct)
        libc.fopen.restype = c_void_p

        try:
            f = libc.fopen("/proc/mounts", "r")
        except:
            try : 
                f = libc.fopen("/etc/mtab", "r")
            except :
                raise IOError("Unable to open /proc/mounts nor /etc/mtab")

        while True:
            entry = libc.getmntent(f)
            if bool(entry) == False: 
                libc.fclose(f)
                break        
            yield Filesystem(entry.contents.mnt_dir, entry.contents.mnt_type, entry.contents.mnt_fsname)

    __mounted_filesystems=staticmethod(__mounted_filesystems)

    # staticmethod
    def all() :
        return [ Volume(elem.mount_dir) for elem in Volume.__mounted_filesystems()]
    all=staticmethod(all)



