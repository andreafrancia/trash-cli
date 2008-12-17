#!/usr/bin/python
# libtrash/__init__.py: library supporting FreeDesktop.org Trash Spec 
#
# Copyright (C) 2007,2008 Andrea Francia Trivolzio(PV) Italy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  
# 02110-1301, USA.

from __future__ import absolute_import

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
import posixpath

logger=logging.getLogger()
#logger.setLevel(0)
logger.setLevel(logging.FATAL)

from .filesystem import Volume
from .filesystem import Path

"""
Represent a trash directory.
For example $XDG_DATA_HOME/Trash
"""
class TrashDirectory(object) :
    def __init__(self, path, volume) :
        assert isinstance(path,Path)
        assert isinstance(volume,Volume)
        self.path = path
        self.volume = volume

    def __str__(self) :
        return str(self.path)

    """ 
    Trash the specified file.
    returns TrashedFile
    """
    def trash(self, file):
        assert(isinstance(file, Path))

        if not self.volume == file.parent.volume :
            raise ("file is not in the same volume of trash directory!\n"
                   + "self.volume = " + str(self.volume) + ", \n"
                   + "file.parent.volume = "
                        + str(file.parent.volume))

        trash_info=TrashInfo(self._path_for_trashinfo(file),datetime.now())
        trash_id=self.persist_trash_info(trash_info)

        if not self.files_dir.exists() : 
            self.files_dir.mkdirs(0700)

        try :
            file.move(self.getOriginalCopyPath(trash_id))
        except IOError, e :
            self.getTrashInfoFile(trash_id).remove();
            raise e

        return TrashedFile(trash_id,trash_info, self)

    @property
    def info_dir(self) :
        return self.path.join("info")

    @property
    def files_dir(self) :
        result=self.path.join("files")
        assert(isinstance(result,Path))
        return result

    def getInfoPath(self) :
        return os.path.join(self.path.path, "info")

    def getFilesPath(self) :
        return os.path.join(self.path.path, "files")

    def trashedFiles(self) :
        try : 
            for trash_info_file in self.info_dir.list() :
                if not trash_info_file.basename.endswith('.trashinfo') :
                    logger.warning("Non .trashinfo file in info dir")
                else :
                    id=self.calc_id(trash_info_file)
                    try:
                        ti=TrashInfo.parse(trash_info_file.read())
                        yield TrashedFile(id,ti,self)
                    except ValueError:
                        logger.warning("Non parsable trashinfo file: %s" % trash_info_file.path)
        except OSError, e: # when directory does not exist
            pass 
    
    @staticmethod
    def calc_id(trash_info_file):
        return trash_info_file.basename[:-len('.trashinfo')]
    
    def trashedFilesInDir(self, dir) :
        dir = os.path.realpath(dir)
        for trashedfile in self.trashedFiles() :
            if trashedfile.path.startswith(dir + Path.sep) :
                yield trashedfile

    def getOriginalCopyPath(self, trashId) :
        return self.getOriginalCopy(trashId).path

    def getOriginalCopy(self, trashId) :
        return Path(os.path.join(self.getFilesPath(), str(trashId)))

    def getTrashInfoFile(self, trashId) :
        return Path(os.path.join(self.getInfoPath(), str(trashId) + '.trashinfo'))

    def removeInfoFile(self, trashId) :
        self.getTrashInfoFile(trashId).remove()

    def _path_for_trashinfo(self, fileToTrash):
        raise NotImplementedError

    """
    Create a .trashinfo file in the $trash/info directory.
    returns the trash_id for the created file.
    """
    def persist_trash_info(self,trash_info) :
        assert(isinstance(trash_info, TrashInfo))

        if not os.path.exists(self.getInfoPath()) : 
            try :
                os.makedirs(self.getInfoPath(), 0700)
            except OSError:
                logging.debug(traceback.print_exc())
                os.makedirs(self.getInfoPath())

        # write trash info
        index = 0
        while True :
            if index == 0 :
                suffix = ""
            elif index < 100:
                suffix = "_%d" % index
            else :
                suffix = "_%d" % random.randint(0, 65535)

            base_id = trash_info.path.basename
            trash_id = base_id + suffix
            trash_info_basename=trash_id+".trashinfo"

            dest = os.path.join(self.getInfoPath(),trash_info_basename)
            try :
                handle = os.open(dest, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0600)
                os.write(handle, trash_info.render())
                os.close(handle)
                logging.debug(".trashinfo created as %s." % dest)
                return trash_id
            except OSError, e:
                logging.debug("Attempt for creating %s failed." % dest)

            index += 1

        raise IOError()

    @staticmethod
    def getHomeTrashDirectory() : 
        if 'XDG_DATA_HOME' in os.environ:
            XDG_DATA_HOME = os.environ['XDG_DATA_HOME']
        else :
            XDG_DATA_HOME = os.environ['HOME'] + '/.local/share'

        path = Path(XDG_DATA_HOME + "/Trash")
        return HomeTrashDirectory(path)

    @classmethod
    def all_trash_directories(cls) :
        """Return a generator of all TrashDirectories in the filesystem"""
        yield TrashDirectory.getHomeTrashDirectory()
        
        for volume in Volume.all():
            yield cls.common_trash_dir(volume)
            yield cls.getUserTrashDirectory(volume)
    
    @staticmethod
    def trashed_files() :
        """Return a generator of all TrashedFiles."""
        for trash_dir in TrashDirectory.all_trash_directories():
            for trashedfile in trash_dir.trashedFiles():
                yield trashedfile

    @classmethod
    def files_trahsed_from_dir(cls,dir) :
        dir = os.path.realpath(dir)
        for trashedfile in cls.trashed_files() :
            if trashedfile.path.path.startswith(dir + os.path.sep) :
                yield trashedfile

    @staticmethod
    def _getuid():
        return os.getuid()

    @classmethod
    def common_trash_dir(cls,volume):
        uid = cls._getuid()
        trash_directory_path = volume.topdir.join(Path(".Trash")).join(Path(str(uid)))
        return VolumeTrashDirectory(trash_directory_path,volume)

    @classmethod
    def getUserTrashDirectory(cls, volume) :
        uid = cls._getuid()
        dirname=".Trash-%s" % str(uid)
        trash_directory_path = volume.topdir.join(Path(dirname))
        return VolumeTrashDirectory(trash_directory_path,volume)
        
class HomeTrashDirectory(TrashDirectory) :
    def __init__(self, path) :
        assert isinstance(path, Path)
        TrashDirectory.__init__(self, path, path.volume)

    def __str__(self) :
        result=TrashDirectory.__str__(self)
        try:
            home_dir=os.environ['HOME']
            home_dir = posixpath.normpath(home_dir)
            if home_dir != '':
                result=re.sub('^'+ re.escape(home_dir)+Path.sep, '~' + Path.sep,result)
        except KeyError:
            pass
        return result

    def _path_for_trashinfo(self, fileToBeTrashed) :
        assert isinstance(fileToBeTrashed, Path)

        # for the HomeTrashDirectory all path are stored as absolute

        parent = fileToBeTrashed.realpath.parent
        return parent.join(fileToBeTrashed.basename)

class VolumeTrashDirectory(TrashDirectory) :
    def __init__(self, path, volume) :
        assert isinstance(path, Path)
        assert isinstance(volume, Volume)
        TrashDirectory.__init__(self,path, volume)

    def _path_for_trashinfo(self, fileToBeTrashed) :
        # for the VolumeTrashDirectory paths are stored as relative 
        # if possible

        # string representing the parent of the fileToBeTrashed
        parent=fileToBeTrashed.parent.realpath
        topdir=self.volume.path   # e.g. /mnt/disk-1

        if parent.path.startswith(topdir.path+Path.sep) :
            parent = Path(parent.path[len(topdir.path+Path.sep):])

        return parent.join(fileToBeTrashed.basename)                      


class TrashedFile (object) :
    def __init__(self,id,trash_info,trash_directory) :
        assert isinstance(id, str)
        assert isinstance(trash_info, TrashInfo)
        assert isinstance(trash_directory, TrashDirectory)
        self.__id=id
        self.__trash_info=trash_info
        self.__trash_directory=trash_directory

    @property
    def id(self) :
        return self.__id
        
    @property
    def path(self) :
        if self.__trash_info.path.isabs() :
            result=self.__trash_info.path
        else :
            result=self.__trash_directory.volume.path.join(self.__trash_info.path)
        assert(isinstance(result, Path))
        return result
    
    @property
    def original_location(self):
        return self.path
    
    @property
    def trash_info(self):
        assert(isinstance(self.__trash_info,TrashInfo))
        return self.__trash_info
    
    @property
    def original_file(self):        
        return self.__trash_directory.getOriginalCopy(self.id)
    
    @property
    def deletion_date(self) :
        return self.__trash_info.getDeletionTime()

    def restore(self) :
        if not self.original_location.exists :
            self.original_location.parent.mkdirs()

        self.original_file.move(self.path)
        self.trash_info_file.remove()

    def purge(self) :
        # created by : Einar Orn Olason
        # 2008-07-26 Andrea Francia: added postcondition test
        self.original_file.remove()
        self.trash_info_file.remove()

    @property
    def trash_info_file(self):
        return self.__trash_directory.getTrashInfoFile(self.id)
    
    @property
    def trash_directory(self) :
        return self.__trash_directory

class TrashInfo (object) :
    def __init__(self, path, deletion_date) :
        """Create a TrashInfo.

        Keyword arguments:
        path          -- the of the .trashinfo file (string or Path)
        deletion_date -- the date of deletion, should be a datetime.
        """
        if  not isinstance(path,Path) :
            path = Path('' + path)
        assert isinstance(deletion_date, datetime)
        self.__path = path
        self.__deletion_date = deletion_date

    def getDeletionTimeAsString(self) :
        return datetime.strftime(self.__deletion_date, "%Y-%m-%dT%H:%M:%S")

    def getDeletionTime(self) :
        return self.__deletion_date

    def path(self) :
        return self.__path
    path = property(path)

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
            path = Path(urllib.unquote(match.groups()[0]))
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
        result += "Path=" + urllib.quote(self.path.path,'/') + "\n"
        result += "DeletionDate=" + self.getDeletionTimeAsString() + "\n"
        return result

class TimeUtils(object):
    @staticmethod
    def parse_iso8601(text) :
        t=time.strptime(text,  "%Y-%m-%dT%H:%M:%S")
        return datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)




