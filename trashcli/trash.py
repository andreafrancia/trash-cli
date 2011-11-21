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
import os
import re
import time
import urllib
import random
from datetime import datetime
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
        path = path.norm()
        self.check()

        if not self.volume == path.parent.volume :
            raise ("file is not in the same volume of trash directory!\n"
                   + "self.volume = " + str(self.volume) + ", \n"
                   + "file.parent.volume = "
                        + str(path.parent.volume))

        trash_info=TrashInfo(self._path_for_trashinfo(path),datetime.now())
        
        basename=trash_info.path.basename
        trashinfo_file_content=trash_info.render()
        (trash_info_file, trash_info_id)=self.persist_trash_info(basename, trashinfo_file_content)

        trashed_file = self._create_trashed_file(trash_info_id,
                                                 path.absolute(),
                                                 trash_info.deletion_date)

        if not self.files_dir.exists() :
            self.files_dir.mkdirs_using_mode(0700)

        try :
            path.move(trashed_file.actual_path)
        except IOError, e :
            remove_file(trash_info_file.path)
            raise e

        return trashed_file

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

    def all_info_files(self) :
	'Returns a generator of "Path"s'
        try :
            for info_file in self.info_dir.list() :
                if not info_file.basename.endswith('.trashinfo') :
                    logger.warning("Non .trashinfo file in info dir")
                else :
		    yield info_file
        except OSError: # when directory does not exist
            pass

    def trashed_files(self) :
        """
        List trashed files.
        Returns a generator for each trashed file in dir.
        """
	for info_file in self.all_info_files():
	    try:
		yield self._create_trashed_file_from_info_file(info_file) 
	    except ValueError:
		logger.warning("Non parsable trashinfo file: %s" % info_file.path)
	    except IOError, e:
		logger.warning(str(e))

    def _create_trashed_file_from_info_file(self,info_file):
	trash_id=self.calc_id(info_file)
	trash_info = TrashInfo.parse(info_file.read())
	path = self._calc_original_location(trash_info.path)

	trashed_file = self._create_trashed_file(trash_id, path,
					trash_info.deletion_date)
	return trashed_file

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
    def persist_trash_info(self,basename,content) :

        self.info_dir.mkdirs_using_mode(0700)
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

            base_id = basename
            trash_id = base_id + suffix
            trash_info_basename=trash_id+".trashinfo"

            dest = self.info_dir.join(trash_info_basename)
            try :
                handle = os.open(dest.path,
                                 os.O_RDWR | os.O_CREAT | os.O_EXCL,
                                 0600)
                os.write(handle, content)
                os.close(handle)
                logger.debug(".trashinfo created as %s." % dest)
                return (dest, trash_id)
            except OSError:
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
        #assert isinstance(fileToBeTrashed, Path)
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


def real_list_mount_points():
    from trashcli.list_mount_points import mount_points
    for mount_point in mount_points(): 
	yield Path(mount_point)
class Directories:
    pass

class GlobalTrashCan(object) :
    """
    Represent the TrashCan that contains all trashed files.
    This class is the facade used by all trashcli commands
    """

    class NullReporter:
	def __getattr__(self,name):
	    return lambda *argl,**args:None
    from datetime import datetime
    def __init__(self, 
		 environ           = os.environ,
		 reporter          = NullReporter(),
		 getuid            = os.getuid,
		 list_mount_points = real_list_mount_points,
		 now               = datetime.now):
	self.getuid            = getuid
	self.environ           = environ
	self.reporter          = reporter
	self.list_mount_points = list_mount_points
	self.now               = now

    def trashed_files(self):
        """Return a generator of all TrashedFile(s)."""
        for trash_dir in self._trash_directories():
            for trashedfile in trash_dir.trashed_files():
                yield trashedfile

    def trash(self,file) :
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
	file=Path(file)	

	if self.should_skipped_by_specs(file):
	    self.reporter.unable_to_trash_dot_entries(file)
	    return
	
	for trash_dir in self._possible_trash_directories_for(file):
	    if self.file_could_be_trashed_in(file, trash_dir.path):
		try:
		    trashed_file = trash_dir.trash(file)
		    self.reporter.file_has_been_trashed_in_as(file, 
								  trashed_file.trash_directory,
								  trashed_file.original_file.path)
		    return

		except (IOError, OSError), error:
		    self.reporter.unable_to_trash_file_in_because(file, trash_dir, error)

	self.reporter.unable_to_trash_file(file)


    def should_skipped_by_specs(self,file):
	return (file.basename == ".") or (file.basename == "..")

    def volume_of_parent(self, file):
	return self.volume_of(self.parent_of(file))

    def file_could_be_trashed_in(self,file_to_be_trashed,trash_dir_path):
	return self.volume_of(trash_dir_path) == self.volume_of_parent(file_to_be_trashed)

    def parent_of(self, file):
	return Path(file.parent)

    def volume_of(self, file):
	return Path(file).volume

    def _trash_directories(self) :
        """Return a generator of all TrashDirectories in the filesystem"""
        yield self._home_trash_dir()
	for mount_point in self.list_mount_points():
	    volume = Volume(mount_point)
            yield self._volume_trash_dir1(volume)
            yield self._volume_trash_dir2(volume)
    def _home_trash_dir(self) :
	return HomeTrashDirectory(Path(self._home_trash_dir_path()))
    def _possible_trash_directories_for(self,file):
	yield self._home_trash_dir()
        for td in self.trash_directories_for_volume(self.volume_of_parent(file)):
            yield td
    def trash_directories_for_volume(self,volume):
        yield self._volume_trash_dir1(volume)
        yield self._volume_trash_dir2(volume) 
    def _volume_trash_dir1(self,volume):
        """
        Return the method (1) volume trash dir ($topdir/.Trash/$uid).
        """
        uid = self.getuid()
        trash_directory_path = volume.topdir.join(Path(".Trash")).join(Path(str(uid)))
        return Method1VolumeTrashDirectory(trash_directory_path,volume)
    def _volume_trash_dir2(self, volume) :
        """
        Return the method (2) volume trash dir ($topdir/.Trash-$uid).
        """
        uid = self.getuid()
        dirname=".Trash-%s" % str(uid)
        trash_directory_path = volume.topdir.join(Path(dirname))
        return VolumeTrashDirectory(trash_directory_path,volume)
    def _home_trash_dir_path(self):
        if 'XDG_DATA_HOME' in self.environ:
            XDG_DATA_HOME = self.environ['XDG_DATA_HOME']
        else :
	    XDG_DATA_HOME = self.environ['HOME'] + '/.local/share'
        return XDG_DATA_HOME + "/Trash"
	

    def for_all_trashed_file(self, action):
        for trashedfile in self.trashed_files():
            action(info_path=trashedfile.original_file.path,
                   path=trashedfile.info_file.path)
    def for_all_files_trashed_more_than(self, days_ago, action):
        for trashedfile in self.trashed_files() :
            delta=self.now()-trashedfile.deletion_date
            if delta.days >= days_ago :
                action(info_path=trashedfile.original_file.path,
                       path=trashedfile.info_file.path)

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
        if self.path.exists():
            raise IOError('Refusing to overwrite existing file "%s".' % self.path.basename);
        else:
            self.path.parent.mkdirs()

        self.original_file.move(self.path)
        remove_file(self.info_file.path)

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
        except IndexError:
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
        except IndexError:
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
class List:
    def __init__(self, out):
        self.out = out

    def main(self, *argv):
        program_name=argv[0]
        import getopt
        options, arguments = getopt.getopt(argv[1:], 'h', ['help'])
    
        for option, value in options:
            if option == '--help':
                self._println("""\
Usage: %s

List trashed files

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues\
""" % program_name)
            return

        trashsystem = GlobalTrashCan()
        for trashed_file in trashsystem.trashed_files() :
            self._println("%s %s" % (trashed_file.deletion_date, trashed_file.path))

    def _println(self,line):
        self.out.write(line)
        self.out.write('\n')

import shutil
def remove_file(path):
    if(os.path.exists(path)):
        try:
            os.remove(path)
        except:
            return shutil.rmtree(path)
import sys
from trashcli.trash import GlobalTrashCan
class EmptyCmd:
    from datetime import datetime
    def __init__(self,
                 now=datetime.now,
                 trashcan=GlobalTrashCan(datetime.now)):
        self.now = now
        self.trashcan = trashcan

    def run(self,argv):
        Parser(Deleter(self.trashcan)).run_with_argv(sys.argv) 

class Parser:
    def __init__(self,deleter):
        self.deleter = deleter
        self.parser = self.get_option_parser()

    def run_with_argv(self,argv):
        (options, args) = self.parser.parse_args(argv[1:])

        if len(args) > 1 :
            self._print_usage()
        elif len(args) == 1 :
            try :
                days=int(args[0])
                self.deleter.delete_files_older_than(days)
            except ValueError:
                self._print_usage()
        else:
            self.deleter.delete_all_files()

    def _print_usage(self):
        self.parser.print_usage()
        self.parser.exit()

    def get_option_parser(self):
        from trashcli import version
        from optparse import OptionParser
        from trashcli.cli.util import NoWrapFormatter

        parser = OptionParser(usage="%prog [days]",
                              description="Purge trashed files.",
                              version="%%prog %s" % version,
                              formatter=NoWrapFormatter(),
                              epilog=
        """Report bugs to http://code.google.com/p/trash-cli/issues""")

        return parser

class Deleter:
    def __init__(self,trashcan):
        self.trashcan = trashcan
    def delete_all_files(self):
        self.trashcan.for_all_trashed_file(self._delete)
    def delete_files_older_than(self, days):
        self.trashcan.for_all_files_trashed_more_than(days_ago=days,
                action=self._delete)
    def _delete(self, info_path, path):
        remove_file(path)
        remove_file(info_path)
