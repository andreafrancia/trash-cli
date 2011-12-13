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

import os
import random
import logging

logger=logging.getLogger('trashcli.trash')
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

#from .filesystem import Volume
#from .filesystem import Path
from .trash2 import contents_of

class TrashDirectory:
    """\
    Represent a trash directory.
    For example $XDG_DATA_HOME/Trash
    """
    def __init__(self, path, volume) :
        assert isinstance(path,Path)
        assert isinstance(volume,Volume)
        self.path = path.norm()
        self.volume = volume

    def __str__(self) :
        return str(self.path)

    def __repr__(self) :
        return "TrashDirectory(\"%s\", \"%s\")" % (self.path, self.volume)

    """\
    Trash the specified file.
    returns the TrashedFile
    """
    def trash(self, path):
        from datetime import datetime
        path = os.path.normpath(path)
        path = Path(path)
        self.check()

        if not self.volume == path.parent.volume :
            raise ("file is not in the same volume of trash directory!\n"
                   + "self.volume = " + str(self.volume) + ", \n"
                   + "file.parent.volume = "
                        + str(path.parent.volume))

        trash_info = TrashInfo(self._path_for_trashinfo(path),
                               datetime.now())
        
        basename = trash_info.path.basename
        trashinfo_file_content = trash_info.render()
        (trash_info_file, trash_info_id) = self.persist_trash_info(basename, 
                                                                   trashinfo_file_content)

        trashed_file = self._create_trashed_file(trash_info_id,
                                                 Path(os.path.abspath(path)),
                                                 trash_info.deletion_date)

        if not self.files_dir.exists() :
            mkdirs_using_mode(self.files_dir, 0700)

        try :
            move(path, trashed_file.actual_path)
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
        result = os.path.join(self.path, 'info')
        result = Path(result)
        return result

    @property
    def files_dir(self):
        """
        The directory where original file where stored.
        A Path instance.
        """
        result = os.path.join(self.path, 'files')
        result = Path(result)
        return result

    def all_info_files(self) :
	'Returns a generator of "Path"s'
        try :
            for info_file in list_files_in_dir(self.info_dir):
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
		logger.warning("Non parsable trashinfo file: %s" % info_file)
	    except IOError, e:
		logger.warning(str(e))

    def _create_trashed_file_from_info_file(self, info_file):
	trash_id = self.calc_id(info_file)
	trash_info = TrashInfo.parse(contents_of(info_file))
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

        mkdirs_using_mode(self.info_dir, 0700)
        os.chmod(self.info_dir,0700)

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
            trash_info_basename = trash_id+".trashinfo"

            dest = os.path.join(self.info_dir, trash_info_basename)
            dest = Path(dest)
            try :
                handle = os.open(dest,
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

class HomeTrashDirectory(TrashDirectory):
    def __init__(self, path) :
        assert isinstance(path, Path)
        TrashDirectory.__init__(self, path, path.volume)

    def __str__(self):
        import re
        import posixpath
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

        parent   = fileToBeTrashed.realpath.parent
        realpath = os.path.realpath(fileToBeTrashed)
        parent   = os.path.dirname(realpath)
        basename = os.path.basename(fileToBeTrashed)
        result   = os.path.join(parent,basename)
        return Path(result)

class VolumeTrashDirectory(TrashDirectory) :
    def __init__(self, path, volume) :
        TrashDirectory.__init__(self,path, volume)

    def _path_for_trashinfo(self, fileToBeTrashed) :
        # for the VolumeTrashDirectory paths are stored as relative
        # if possible
        fileToBeTrashed = fileToBeTrashed.norm()

        # string representing the parent of the fileToBeTrashed
        parent = os.path.dirname(fileToBeTrashed)
        parent = os.path.realpath(parent)

        topdir=self.volume.path   # e.g. /mnt/disk-1

        if parent.startswith(topdir.path+os.path.sep) :
            parent = Path(parent[len(topdir.path+os.path.sep):])

        result = os.path.join(parent, os.path.basename(fileToBeTrashed))
        result = Path(result)
        return result

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
        if not self.parent_is_dir():
            raise TopDirNotPresent("topdir should be a directory: %s"
                                   % self.path)
        if self.parent_is_link():
            raise TopDirIsSymLink("topdir can't be a symbolic link: %s"
                                  % self.path)
        if not self.parent_has_sticky_bit():
            raise TopDirWithoutStickyBit("topdir should have the sticky bit: %s"
                                         % self.path)
    def parent_is_dir(self):
        return os.path.isdir(self.parent())
    def parent_is_link(self):
        return os.path.islink(self.parent())
    def parent(self):
        return os.path.dirname(self.path)
    def parent_has_sticky_bit(self):
        return has_sticky_bit(self.parent())

def real_list_mount_points():
    from trashcli.list_mount_points import mount_points
    for mount_point in mount_points(): 
	yield Path(mount_point)

class GlobalTrashCan:
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

class TrashedFile:
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

        move(self.original_file, self.path)
        remove_file(self.info_file.path)

    @property
    def info_file(self):
        return self._info_file

    @property
    def trash_directory(self) :
        return self._trash_directory

class TrashInfo:
    def __init__(self, path, deletion_date):
        from datetime import datetime
        """Create a TrashInfo.

        Keyword arguments:
        path          -- the of the .trashinfo file (string or Path)
        deletion_date -- the date of deletion, should be a datetime.
        """
        if not isinstance(path,Path):
            path = Path('' + path)
        if not isinstance(deletion_date, datetime):
            raise TypeError("deletion_date should be a datetime")
        self._path = path
        self._deletion_date = deletion_date

    @staticmethod
    def _format_date(deletion_date):
        return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def deletion_date(self):
        return self._deletion_date

    @property
    def path(self):
        return self._path

    @staticmethod
    def parse(data):
        from StringIO import StringIO
        import urllib
        import re
        path = None
        deletion_date = None

        stream = StringIO(data)
        line = stream.readline().rstrip('\n')
        if line != "[Trash Info]":
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
        import urllib
        result = "[Trash Info]\n"
        result += "Path=" + urllib.quote(self.path.path,'/') + "\n"
        result += "DeletionDate=" + self._format_date(self.deletion_date) + "\n"
        return result

class TimeUtils:
    @staticmethod
    def parse_iso8601(text) :
        import time
        from datetime import datetime
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

class RestoreCmd:
    def __init__(self):
        pass
    def run(self):
        trashcan = GlobalTrashCan()

        def is_trashed_from_curdir(trashedfile):
            dir = os.path.realpath(os.curdir)
            if trashedfile.path.path.startswith(dir + os.path.sep) :
                return True

        trashed_files = []
        i = 0
        for trashedfile in filter(is_trashed_from_curdir, trashcan.trashed_files()) :
            trashed_files.append(trashedfile)
            print "%4d %s %s" % (i, trashedfile.deletion_date, trashedfile.path)
            i += 1

        if len(trashed_files) == 0 :
            print "No files trashed from current dir ('%s')" % os.path.realpath(os.curdir)
        else :
            index=raw_input("What file to restore [0..%d]: " % (len(trashed_files)-1))
            if index == "" :
                print "Exiting"
            else :
                index = int(index)
                try:
                    trashed_files[index].restore()
                except IOError, e:
                    import sys
                    print >> sys.stderr, str(e)
                    sys.exit(1)	

from optparse import IndentedHelpFormatter
class NoWrapFormatter(IndentedHelpFormatter) :
    def _format_text(self, text) :
        "[Does not] format a text, return the text as it is."
        return text

class TrashPutCmd:
    def __init__(self, stdout, stderr):
	self.stdout=stdout
	self.stderr=stderr

    def run(self,argv):
	parser = self.get_option_parser()
	(options, args) = parser.parse_args(argv[1:])

	if len(args) <= 0:
	    parser.error("Please specify the files to trash.")

	reporter=TrashPutReporter(self.get_logger(options.verbose,argv[0]))

	self.trashcan=GlobalTrashCan(reporter=reporter)
	self.trash_all(args)

    def trash_all(self, args):
	for arg in args :
	    self.trash(arg)

    def trash(self, arg):
	self.trashcan.trash(Path(arg))

    def get_option_parser(self):
	from trashcli import version
	from optparse import OptionParser

	parser = OptionParser(usage="%prog [OPTION]... FILE...",
			      description="Put files in trash",
			      version="%%prog %s" % version,
			      formatter=NoWrapFormatter(),
			      epilog=
"""To remove a file whose name starts with a `-', for example `-foo',
use one of these commands:

    trash -- -foo

    trash ./-foo

Report bugs to http://code.google.com/p/trash-cli/issues""")
	parser.add_option("-d",
			  "--directory",
			  action="store_true",
			  help="ignored (for GNU rm compatibility)")
	parser.add_option("-f",
			  "--force",
			  action="store_true",
			  help="ignored (for GNU rm compatibility)")
	parser.add_option("-i",
			  "--interactive",
			  action="store_true",
			  help="ignored (for GNU rm compatibility)")
	parser.add_option("-r",
			  "-R",
			  "--recursive",
			  action="store_true",
			  help="ignored (for GNU rm compatibility)")
	parser.add_option("-v",
			  "--verbose",
			  action="store_true",
			  help="explain what is being done",
			  dest="verbose")
	return parser

    def get_logger(self,verbose,argv0):
	import os.path
	class MyLogger:
	    def __init__(self, stderr):
		self.program_name = os.path.basename(argv0)
		self.stderr=stderr
	    def info(self,message):
		if verbose:
		    self.emit(message)
	    def warning(self,message):
		self.emit(message)
	    def emit(self, message):
		self.stderr.write("%s: %s\n" % (self.program_name,message))
	
	return MyLogger(self.stderr)

class TrashPutReporter:
    def __init__(self, logger):
	self.logger = logger

    def unable_to_trash_dot_entries(self,file):
	self.logger.warning("cannot trash %s `%s'" % (file.type_description(), file))

    def unable_to_trash_file(self,f):
	self.logger.warning("cannot trash %s `%s'" % (f.type_description(), f))

    def file_has_been_trashed_in_as(self, trashee, trash_directory, destination):
	self.logger.info("`%s' trashed in %s " % (trashee, trash_directory))

    def unable_to_trash_file_in_because(self, file_to_be_trashed, trash_directory, error):
	self.logger.info("Failed to trash %s in %s, because :%s" % (file_to_be_trashed,
	    trash_directory, error))

def mkdirs_using_mode(path, mode):
    if os.path.isdir(path):
        os.chmod(path, mode)
        return
    os.makedirs(path, mode)

def list_files_in_dir(path):
    for entry in os.listdir(path):
        result = os.path.join(path, entry)
        result = Path(result)
        yield result

def move(path, dest) :
    import shutil
    return shutil.move(path, str(dest))

def has_sticky_bit(path):
    import os
    import stat
    return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX
import os
import shutil
import unipath

class Path (unipath.Path) :
    sep = '/'

    @property
    def path(self):
        return str(self)

    @property
    def parent(self) :
        return Path(os.path.dirname(self.path))

    @property
    def realpath(self) :
        return Path(os.path.realpath(self.path))

    @property
    def basename(self) :
        return self.name

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
        else:
            return self.__join_str(str(path))

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

    def isabs(self) :
        return os.path.isabs(self.path)

    def __eq__(self, other) :
        if self is other:
            return True
        if self.path == other:
            return True
        return False

    def mkdir(self):
        os.mkdir(self.path)

    def mkdirs(self):
        if self.isdir():
            return
        os.makedirs(self.path)

    def __repr__(self):
        return "Path('%s')" % self.path

    def type_description(self):
        """
        Return a textual description of the file pointed by this path.
        Options:
         - "symbolic link"
         - "directory"
         - "`.' directory"
         - "`..' directory"
         - "regular file"
         - "regular empty file"
         - "entry"
        """
        if os.path.islink(self):
            return 'symbolic link'
        elif os.path.isdir(self):
            if self == '.':
                return 'directory'
            elif self == '..':
                return 'directory'
            else:
                if os.path.basename(self) == '.':
                    return "`.' directory"
                elif os.path.basename(self) == '..':
                    return "`..' directory"
                else:
                    return 'directory'
        elif os.path.isfile(self):
            if os.path.getsize(self) == 0:
                return 'regular empty file'
            else:
                return 'regular file'
        else:
            return 'entry'


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

    @staticmethod
    def volume_of(path) :
        path = os.path.realpath(path)
        while path != os.path.dirname(path):
            if os.path.ismount(path):
                break
            path = os.path.dirname(path)
        return Volume(Path(path))

    def __repr__(self):
        return "[Path:%s]" % self.path

    @staticmethod
    def all() :
	from trashcli.list_mount_points import mount_points
        for mount_point in mount_points():
            yield Volume(Path(mount_point))


