#!/usr/bin/python
# trashcli/trash.py: library supporting FreeDesktop.org Trash Spec 
#
# Copyright (C) 2007-2009 Andrea Francia Trivolzio(PV) Italy
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

logger=logging.getLogger('trashcli.trash')
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

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
        self.path = path.norm()
        self.volume = volume

    def __str__(self) :
        return str(self.path)

    def __repr__(self) :
        return "TrashDirectory(\"%s\", \"%s\")" % (self.path, self.volume)
    
    """ 
    Trash the specified file.
    returns the TrashedFile
    """
    def trash(self, path):
        assert(isinstance(path, Path))
        path = path.norm()
        self.check()
        
        if not self.volume == path.parent.volume :
            raise ("file is not in the same volume of trash directory!\n"
                   + "self.volume = " + str(self.volume) + ", \n"
                   + "file.parent.volume = "
                        + str(path.parent.volume))

        trash_info=TrashInfo(self._path_for_trashinfo(path),datetime.now())
        
        (trash_info_file, trash_info_id)=self.persist_trash_info(trash_info)
        
        trashed_file = self._create_trashed_file(trash_info_id, 
                                                 path.absolute(), 
                                                 trash_info.deletion_date)
        
        if not self.files_dir.exists() : 
            self.files_dir.mkdirs(0700)

        try :
            path.move(trashed_file.actual_path)
        except IOError, e :
            trash_info_file.remove();
            raise e
        
        return trashed_file
    
    @property
    def info_dir(self) :
        return self.path.join("info")

    @property
    def files_dir(self) :
        result=self.path.join("files")
        assert(isinstance(result,Path))
        return result

    @property
    def info_dir(self):
        """
        The $trash_dir/info dir that contains the .trashinfo files
        as filesystem.Path.
        """
        return self.path.join("info")
    
    @property
    def files_dir(self):
        """
        The directory where original file where stored. 
        A Path instance.
        """
        return self.path.join("files")

    def trashed_files(self) :
        """
        List trashed files.
        Returns a generator for each trashed file in dir.
        """
        try : 
            for info_file in self.info_dir.list() :
                if not info_file.basename.endswith('.trashinfo') :
                    logger.warning("Non .trashinfo file in info dir")
                else :
                    trash_id=self.calc_id(info_file)
                    try:
                        trash_info = TrashInfo.parse(info_file.read())
                        path = self._calc_original_location(trash_info.path)
                        
                        yield self._create_trashed_file(trash_id, path, 
                                                        trash_info.deletion_date)
                    except ValueError:
                        logger.warning("Non parsable trashinfo file: %s" 
                                       % info_file.path)
                    except IOError, e:
                        logger.warning(str(e))
        except OSError, e: # when directory does not exist
            pass 

    def _create_trashed_file(self, trash_id, path, deletion_date):
        actual_path = self._calc_path_for_actual_file(trash_id)
        info_file = self._calc_path_for_info_file(trash_id)
        
        return TrashedFile(path, 
                           deletion_date,
                           info_file, 
                           actual_path, 
                           self)
                            
    def _calc_original_location(self, path):
        if path.isabs() :
            return path
        else :
            return self.volume.path.join(path)
        
    @staticmethod
    def calc_id(trash_info_file):
        return trash_info_file.basename[:-len('.trashinfo')]
    
    def _calc_path_for_actual_file(self, trash_id) :
        return self.files_dir.join(trash_id)

    def _calc_path_for_info_file(self, trash_id) :
        return self.info_dir.join('%s.trashinfo' % trash_id)

    def _path_for_trashinfo(self, fileToTrash):
        raise NotImplementedError()

    """
    Create a .trashinfo file in the $trash/info directory.
    returns the created TrashInfoFile.
    """
    def persist_trash_info(self,trash_info) :
        assert(isinstance(trash_info, TrashInfo))
        
        self.info_dir.mkdirs(0700)
        self.info_dir.chmod(0700)
        
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

            dest = self.info_dir.join(trash_info_basename)
            try :
                handle = os.open(dest.path, 
                                 os.O_RDWR | os.O_CREAT | os.O_EXCL, 
                                 0600)
                os.write(handle, trash_info.render())
                os.close(handle)
                logger.debug(".trashinfo created as %s." % dest)
                return (dest, trash_id)
            except OSError, e:
                logger.debug("Attempt for creating %s failed." % dest)

            index += 1

        raise IOError()

    def check(self):
        """
        Perform a sanity check of this trash directory.
        If the check is not passed the directory can be used for trashing, 
        listing or restoring files.
        """
        pass
        
class HomeTrashDirectory(TrashDirectory) :
    def __init__(self, path) :
        assert isinstance(path, Path)
        logger.debug("HomeTrashDirectory with path = %s" % path)
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
        fileToBeTrashed = fileToBeTrashed.norm()
        
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
        fileToBeTrashed = fileToBeTrashed.norm()
        
        # string representing the parent of the fileToBeTrashed
        parent=fileToBeTrashed.parent.realpath
        topdir=self.volume.path   # e.g. /mnt/disk-1

        if parent.path.startswith(topdir.path+Path.sep) :
            parent = Path(parent.path[len(topdir.path+Path.sep):])

        return parent.join(fileToBeTrashed.basename)

class TopDirWithoutStickyBit(IOError):
    """
    Raised when $topdir/.Trash doesn't have the sticky bit.
    """
    pass

class TopDirNotPresent(IOError):
    """
    Raised when $topdir/.Trash is not a dir.
    """
    pass

class TopDirIsSymLink(IOError):
    """
    Raised when $topdir/.Trash is a simbolic link.
    """
    pass

class Method1VolumeTrashDirectory(VolumeTrashDirectory):
    def __init__(self, path, volume) :
        VolumeTrashDirectory.__init__(self,path,volume)
        
    def check(self):
        if not self.path.parent.isdir():
            raise TopDirNotPresent("topdir should be a directory: %s" 
                                   % self.path)
        if self.path.parent.islink():
            raise TopDirIsSymLink("topdir can't be a symbolic link: %s" 
                                  % self.path)
        if not self.path.parent.has_sticky_bit():
            raise TopDirWithoutStickyBit("topdir should have the sticky bit: %s"
                                         % self.path)

class TrashCan(object):
    def trashed_files(self):
        pass

    def trash(self, file):
        pass

class GlobalTrashCan(TrashCan) :
    """
    Represent the TrashCan that contains all trashed files.
    This class is the facade used by all trashcli commands
    """

    def __init__(self, fake_uid=None) :
        self.fake_uid = fake_uid
    
    def _getuid(self):
        if self.fake_uid is None:
            return os.getuid()
        else:
            return self.fake_uid
        
    def trashed_files(self):
        """Return a generator of all TrashedFile(s)."""
        for trash_dir in self.trash_directories():
            for trashedfile in trash_dir.trashed_files():
                yield trashedfile

    def trashed_file(self, name):
        pass
    
    def trash (self,f) :
        """ 
        Trash a file in the appropriate trash directory.
        If the file belong to the same volume of the trash home directory it 
        will be trashed in the home trash directory.
        Otherwise it will be trashed in one of the relevant volume trash 
        directories.
        
        Each volume can have two trash directories, they are 
            - $volume/.Trash/$uid
            - $volume/.Trash-$uid
        
        Firstly the software attempt to trash the file in the first directory 
        then try to trash in the second trash directory.
        """
        volume = f.parent.volume
    
        if self.home_trash_dir().volume == volume :
            trashed_file = self.home_trash_dir().trash(f)
        else :
            volume_trash_dir1 = self.volume_trash_dir1(volume)
            try:
                trashed_file = volume_trash_dir1.trash(f)
            except (IOError, OSError), e:
                logger.debug("Trashing in method(1) trash dir failed: %s" %e)
                trashed_file = self.volume_trash_dir2(volume).trash(f)
        
        logger.info("File trashed as: `%s'" % (trashed_file.original_file.path))
        assert(isinstance(trashed_file, TrashedFile))
        return trashed_file

    def trash_directories(self) :
        """Return a generator of all TrashDirectories in the filesystem"""
        
        yield self.home_trash_dir()
        for volume in Volume.all():
            yield self.volume_trash_dir1(volume)
            yield self.volume_trash_dir2(volume)

    def home_trash_dir(self) : 
        if 'XDG_DATA_HOME' in os.environ:
            XDG_DATA_HOME = os.environ['XDG_DATA_HOME']
        else :
            XDG_DATA_HOME = os.environ['HOME'] + '/.local/share'

        path = Path(XDG_DATA_HOME + "/Trash")
        return HomeTrashDirectory(path)

    def volume_trash_dir1(self,volume):
        """
        Return the method (1) volume trash dir ($topdir/.Trash/$uid).
        """
        uid = self._getuid()
        trash_directory_path = volume.topdir.join(Path(".Trash")).join(Path(str(uid)))
                
        return Method1VolumeTrashDirectory(trash_directory_path,volume)

    def volume_trash_dir2(self, volume) :
        """
        Return the method (2) volume trash dir ($topdir/.Trash-$uid).
        """
        uid = self._getuid()
        dirname=".Trash-%s" % str(uid)
        trash_directory_path = volume.topdir.join(Path(dirname))
        return VolumeTrashDirectory(trash_directory_path,volume)


class TrashedFile(object) :
    """
    Represent a trashed file.
    Each trashed file is persisted in two files:
     - $trash_dir/info/$id.trashinfo
     - $trash_dir/files/$id
    
    Properties:
     - path : the original path from where the file has been trashed
     - deletion_date : the time when the file has been trashed (instance of 
                       datetime)
     - info_file : the file that contains information (instance of Path)
     - actual_path : the path where the trashed file has been placed after the 
                     trash opeartion (instance of Path)
     - trash_directory : 
    """
    def __init__(self, 
                 path, 
                 deletion_date, 
                 info_file, 
                 actual_path, 
                 trash_directory) :
        
        if not hasattr(actual_path,'move'):
            raise TypeError('actual_path should have move(). '
                            'Tip: use a Path instance.')

        if not hasattr(actual_path,'remove'):
            raise TypeError('actual_path should have remove(). '
                            'Tip: use a Path instance.')
        
        if not hasattr(info_file,'remove'):
            raise TypeError('info_file should have remove(). '
                            'Tip: use a Path instance.')

        if not Path('' + path).isabs():
            raise ValueError("Absolute path required.")
        
        self._path = path
        self._deletion_date = deletion_date
        self._info_file = info_file
        self._actual_path = actual_path
        self._trash_directory = trash_directory

    @property
    def path(self) :
        """
        The path from where the file has been trashed
        """
        return self._path
    
    @property
    def actual_path(self):        
        return self._actual_path
    
    original_file = actual_path
    
    @property
    def deletion_date(self) :
        return self._deletion_date

    def restore(self, dest=None) :
        if dest is not None:
            raise NotImplementedError("not yet supported")
        if not self.path.exists() :
            self.path.parent.mkdirs()

        self.original_file.move(self.path)
        self.info_file.remove()

    def purge(self) :
        # created by : Einar Orn Olason
        # 2008-07-26 Andrea Francia: added postcondition test
        self.original_file.remove()
        self.info_file.remove()

    @property
    def info_file(self):
        return self._info_file
    
    @property
    def trash_directory(self) :
        return self._trash_directory

class TrashInfo (object) :
    def __init__(self, path, deletion_date) :
        """Create a TrashInfo.

        Keyword arguments:
        path          -- the of the .trashinfo file (string or Path)
        deletion_date -- the date of deletion, should be a datetime.
        """
        if not isinstance(path,Path) :
            path = Path('' + path)
        if not isinstance(deletion_date, datetime):
            raise TypeError("deletion_date should be a datetime")
        self._path = path
        self._deletion_date = deletion_date

    @staticmethod
    def _format_date(deletion_date) : 
        return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def deletion_date(self) :
        return self._deletion_date

    @property
    def path(self) :
        return self._path

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
        result += "DeletionDate=" + self._format_date(self.deletion_date) + "\n"
        return result

class TimeUtils(object):
    @staticmethod
    def parse_iso8601(text) :
        t=time.strptime(text,  "%Y-%m-%dT%H:%M:%S")
        return datetime(t.tm_year, t.tm_mon, t.tm_mday, 
                        t.tm_hour, t.tm_min, t.tm_sec)

trashcan = GlobalTrashCan()
