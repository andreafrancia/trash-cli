# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

from __future__ import absolute_import

import os
import random
import logging

logger=logging.getLogger('trashcli.trash')
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

class TrashDirectory:
    def __init__(self, path, volume) :
        self.path = os.path.normpath(path)
        self.volume = volume

    def __str__(self) :
        return str(self.path)

    def trash(self, path):
        from datetime import datetime
        path = os.path.normpath(path)
        self.check()

        if not self.volume == volume_of(parent_of(path)) :
            raise IOError("file is not in the same volume of trash directory!\n"
                   + "self.volume = " + str(self.volume) + ", \n"
                   + "file.parent.volume = "
                        + str(volume_of(parent_of(path))))

        trash_info = TrashInfo(self._path_for_trashinfo(path),
                               datetime.now())
        
        basename = os.path.basename(trash_info.path)
        trashinfo_file_content = trash_info.render()
        (trash_info_file, trash_info_id) = self.persist_trash_info(basename, 
                                                                   trashinfo_file_content)

        trashed_file = self._create_trashed_file(trash_info_id,
                                                 os.path.abspath(path),
                                                 trash_info.deletion_date)

        self.ensure_files_dir_exists()

        try :
            move(path, trashed_file.actual_path)
        except IOError, e :
            remove_file(trash_info_file)
            raise e

        return trashed_file

    def ensure_files_dir_exists(self):
        if not os.path.exists(self.files_dir) :
            mkdirs_using_mode(self.files_dir, 0700)

    @property
    def info_dir(self):
        """
        The $trash_dir/info dir that contains the .trashinfo files
        as filesystem.Path.
        """
        result = os.path.join(self.path, 'info')
        return result

    @property
    def files_dir(self):
        """
        The directory where original file where stored.
        A Path instance.
        """
        result = os.path.join(self.path, 'files')
        return result

    def all_info_files(self) :
	'Returns a generator of "Path"s'
        try :
            for info_file in list_files_in_dir(self.info_dir):
                if not os.path.basename(info_file).endswith('.trashinfo') :
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
        info_file   = self._calc_path_for_info_file(trash_id)

        return TrashedFile(path,
                           deletion_date,
                           info_file,
                           actual_path,
                           self)

    def _calc_original_location(self, path):
        if os.path.isabs(path) :
            return path
        else :
            return os.path.join(self.volume, path)

    @staticmethod
    def calc_id(trash_info_file):
        return os.path.basename(trash_info_file)[:-len('.trashinfo')]

    def _calc_path_for_actual_file(self, trash_id) :
        return os.path.join(self.files_dir, trash_id)

    def _calc_path_for_info_file(self, trash_id) :
        return os.path.join(self.info_dir, '%s.trashinfo' % trash_id)

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
        TrashDirectory.__init__(self, path, volume_of(path))

    def __str__(self):
        import re
        import posixpath
        result=TrashDirectory.__str__(self)
        try:
            home_dir=os.environ['HOME']
            home_dir = posixpath.normpath(home_dir)
            if home_dir != '':
                result=re.sub('^'+ re.escape(home_dir)+os.path.sep, '~' + os.path.sep,result)
        except KeyError:
            pass
        return result

    def _path_for_trashinfo(self, fileToBeTrashed) :
        fileToBeTrashed = os.path.normpath(fileToBeTrashed)

        # for the HomeTrashDirectory all path are stored as absolute

        realpath = os.path.realpath(fileToBeTrashed)
        parent   = os.path.dirname(realpath)
        basename = os.path.basename(fileToBeTrashed)
        result   = os.path.join(parent,basename)

        return result

class VolumeTrashDirectory(TrashDirectory) :
    def __init__(self, path, volume) :
        TrashDirectory.__init__(self,path, volume)

    def _path_for_trashinfo(self, fileToBeTrashed) :
        # for the VolumeTrashDirectory paths are stored as relative
        # if possible
        fileToBeTrashed = os.path.normpath(fileToBeTrashed)

        # string representing the parent of the fileToBeTrashed
        parent = os.path.dirname(fileToBeTrashed)
        parent = os.path.realpath(parent)

        topdir=self.volume   # e.g. /mnt/disk-1

        if parent.startswith(topdir+os.path.sep) :
            parent = parent[len(topdir+os.path.sep):]

        result = os.path.join(parent, os.path.basename(fileToBeTrashed))
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
	yield mount_point

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

	if self.should_skipped_by_specs(file):
	    self.reporter.unable_to_trash_dot_entries(file)
	    return
	
	for trash_dir in self._possible_trash_directories_for(file):
	    if self.file_could_be_trashed_in(file, trash_dir.path):
		try:
		    trashed_file = trash_dir.trash(file)
		    self.reporter.file_has_been_trashed_in_as(
                          file, 
                          trashed_file.trash_directory,
                          trashed_file.original_file)
		    return

		except (IOError, OSError), error:
		    self.reporter.unable_to_trash_file_in_because(file, trash_dir, error)

	self.reporter.unable_to_trash_file(file)

    def should_skipped_by_specs(self, file):
        basename = os.path.basename(file)
	return (basename == ".") or (basename == "..")

    def volume_of_parent(self, file):
	return volume_of(parent_of(file))

    def file_could_be_trashed_in(self,file_to_be_trashed,trash_dir_path):
	return volume_of(trash_dir_path) == self.volume_of_parent(file_to_be_trashed)

    def _trash_directories(self) :
        """Return a generator of all TrashDirectories in the filesystem"""
        yield self._home_trash_dir()
	for mount_point in self.list_mount_points():
	    volume = mount_point
            yield self._volume_trash_dir1(volume)
            yield self._volume_trash_dir2(volume)
    def _home_trash_dir(self) :
	return HomeTrashDirectory(self._home_trash_dir_path())
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
        trash_directory_path = os.path.join(volume, '.Trash', str(uid))
        return Method1VolumeTrashDirectory(trash_directory_path,volume)
    def _volume_trash_dir2(self, volume) :
        """
        Return the method (2) volume trash dir ($topdir/.Trash-$uid).
        """
        uid = self.getuid()
        dirname=".Trash-%s" % str(uid)
        trash_directory_path = os.path.join(volume, dirname)
        return VolumeTrashDirectory(trash_directory_path,volume)
    def _home_trash_dir_path(self):
        if 'XDG_DATA_HOME' in self.environ:
            XDG_DATA_HOME = self.environ['XDG_DATA_HOME']
        else :
	    XDG_DATA_HOME = self.environ['HOME'] + '/.local/share'
        return XDG_DATA_HOME + "/Trash"
	

    def for_all_trashed_file(self, action):
        for trashedfile in self.trashed_files():
            action(
                    info_path = trashedfile.original_file,
                    path      = trashedfile.info_file)

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

        if not os.path.isabs(path):
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
        if os.path.exists(self.path): 
            raise IOError('Refusing to overwrite existing file "%s".' % os.path.basename(self.path))
        else:
            parent = os.path.dirname(self.path)
            mkdirs(parent)

        move(self.original_file, self.path)
        remove_file(self.info_file)

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
            path = urllib.unquote(match.groups()[0])
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
        result += "Path=" + urllib.quote(self.path,'/') + "\n"
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

from . import version

class TrashPutCmd:
    def __init__(self, stdout, stderr, environ = os.environ):
	self.stdout  = stdout
	self.stderr  = stderr
	self.environ = environ

    def run(self, argv):
	parser = self.get_option_parser(os.path.basename(argv[0]))
	(options, args) = parser.parse_args(argv[1:])

	if len(args) <= 0:
	    parser.error("Please specify the files to trash.")

	reporter=TrashPutReporter(self.get_logger(options.verbose,argv[0]))

	self.trashcan = GlobalTrashCan(
                reporter = reporter,
                environ  = self.environ)
	self.trash_all(args)

    def trash_all(self, args):
	for arg in args :
	    self.trash(arg)

    def trash(self, arg):
        self.trashcan.trash(arg)

    def get_option_parser(self, program_name):
	from optparse import OptionParser

	parser = OptionParser(prog=program_name,
                              usage="%prog [OPTION]... FILE...",
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
        def patched_print_help():
            encoding = parser._get_encoding(self.stdout)
            self.stdout.write(parser.format_help().encode(encoding, "replace"))
        def patched_error(msg):
            parser.print_usage(self.stderr)
            parser.exit(2, "%s: error: %s\n" % (program_name, msg))
        def patched_exit(status=0, msg=None):
            if msg: self.stderr.write(msg)
            import sys
            sys.exit(status)

        parser.print_help = patched_print_help
        parser.error = patched_error
        parser.exit = patched_exit
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
	self.logger.warning("cannot trash %s `%s'" % (describe(file), file))

    def unable_to_trash_file(self,f):
	self.logger.warning("cannot trash %s `%s'" % (describe(f), f))

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
        yield result

def move(path, dest) :
    import shutil
    return shutil.move(path, str(dest))

def mkdirs(path):
    if os.path.isdir(path):
        return
    os.makedirs(path)

import os

def parent_of(path):
    return os.path.dirname(path)

def describe(path):
    """
    Return a textual description of the file pointed by this path.
    Options:
     - "symbolic link"
     - "directory"
     - "`.' directory"
     - "`..' directory"
     - "regular file"
     - "regular empty file"
     - "non existent"
     - "entry"
    """
    if os.path.islink(path):
        return 'symbolic link'
    elif os.path.isdir(path):
        if path == '.':
            return 'directory'
        elif path == '..':
            return 'directory'
        else:
            if os.path.basename(path) == '.':
                return "`.' directory"
            elif os.path.basename(path) == '..':
                return "`..' directory"
            else:
                return 'directory'
    elif os.path.isfile(path):
        if os.path.getsize(path) == 0:
            return 'regular empty file'
        else:
            return 'regular file'
    elif not os.path.exists(path):
        return 'non existent'
    else:
        return 'entry'

def volume_of(path) :
    path = os.path.realpath(path)
    while path != os.path.dirname(path):
        if os.path.ismount(path):
            break
        path = os.path.dirname(path)
    return path

def write_file(path, contents):
    f = open(path, 'w')
    f.write(contents)
    f.close()

def do_nothing(*argv, **argvk): pass
class _FileReader:
    def __init__(self):
        self.contents_of = contents_of
        self.exists = os.path.exists
        self.is_sticky_dir = is_sticky_dir
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry

def is_sticky_dir(path):
    import os
    return os.path.isdir(path) and has_sticky_bit(path)

def contents_of(path):
    return file(path).read()

class _FileRemover:
    def remove_file(self, path):
        return os.remove(path)
    def remove_file_if_exists(self,path):
        if os.path.exists(path): self.remove_file(path)

from .list_mount_points import mount_points
from . import version
from datetime import datetime

class ListCmd():
    def __init__(self, out, err, environ, 
                 getuid        = os.getuid,
                 list_volumes  = mount_points,
                 is_sticky_dir = is_sticky_dir,
                 file_reader   = _FileReader(),
                 version       = version):

        self.out         = out
        self.err         = err
        self.file_reader = file_reader
        self.infodirs    = AvailableTrashDir(environ, getuid, list_volumes,
                                             is_sticky_dir)
        self.version     = version

    def run(self, *argv):
        parse=Parser()
        parse.on_help(PrintHelp(self.description, self.println))
        parse.on_version(PrintVersion(self.println, self.version))
        parse.as_default(self.list_trash)
        parse(argv)
    def list_trash(self):
        self.infodirs.for_each_infodir(self.file_reader,
                                       self.list_contents)
    def description(self, program_name, printer):
        printer.usage('Usage: %s [OPTIONS...]' % program_name)
        printer.summary('List trashed files')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()
    def list_contents(self, info_dir):
        info_dir.each_parsed_trashinfo(
                on_parse       = self.print_entry,
                on_read_error  = self.print_read_error,
                on_parse_error = self.print_parse_error)
    def print_parse_error(self, offending_file, reason):
        self.error("Parse Error: %s: %s" % (offending_file, reason))
    def print_read_error(self, error):
        self.error(str(error))
    def print_entry(self, maybe_deletion_date, original_location):
        self.println("%s %s" %(maybe_deletion_date,
                               original_location))
    def println(self, line):
        self.out.write(line+'\n')
    def error(self, line):
        self.err.write(line+'\n')

class Parser:
    def __init__(self):
        self.default_action = do_nothing
        self.argument_action = do_nothing
        self.short_options = ''
        self.long_options = []
        self.actions = dict()
    def __call__(self, argv):
        program_name = argv[0]
        from getopt import getopt
        options, arguments = getopt(argv[1:], 
                                    self.short_options, 
                                    self.long_options)
    
        for option, value in options:
            if option in self.actions:
                self.actions[option](program_name)
                return
        for argument in arguments:
            self.argument_action(argument)
        self.default_action()
    def on_help(self, action):
        self.add_option('help', action, 'h')

    def on_version(self, action):
        self.add_option('version', action)

    def add_option(self, long_option, action, short_aliases=''):
        self.long_options.append(long_option)
        self.actions['--' + long_option] = action
        for short_alias in short_aliases:
            self.add_short_option(short_alias, action)

    def add_short_option(self, short_option, action):
        self.short_options += short_option
        self.actions['-' + short_option] = action

    def on_argument(self, argument_action):
        self.argument_action = argument_action
    def as_default(self, default_action):
        self.default_action = default_action

class EmptyCmd():
    def __init__(self, out, err, environ, 
                 now           = datetime.now,
                 file_reader   = _FileReader(),
                 list_volumes  = mount_points,
                 getuid        = os.getuid,
                 is_sticky_dir = is_sticky_dir,
                 file_remover  = _FileRemover(),
                 version       = version):

        self.out          = out
        self.err          = err
        self.file_reader  = file_reader 
        self.infodirs     = AvailableTrashDir(environ, getuid, list_volumes,
                                              is_sticky_dir)

        self.now          = now
        self.file_remover = file_remover
        self.version      = version

    def run(self, *argv):
        self.date_criteria = always
        parse = Parser()
        parse.on_help(PrintHelp(self.description, self.println))
        parse.on_version(PrintVersion(self.println, self.version))
        parse.on_argument(self.set_deletion_date_criteria)
        parse.as_default(self._delete_according_criteria)
        parse(argv)

    def set_deletion_date_criteria(self, arg):
        self.date_criteria = OlderThan(int(arg), self.now)

    def description(self, program_name, printer):
        printer.usage('Usage: %s [days]' % program_name)
        printer.summary('Purge trashed files.')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()
    def is_int(self, text):
        try:
            int(text)
            return True
        except ValueError:
            return False
    def _delete_according_criteria(self):
        self.infodirs.for_each_infodir(self.file_reader,
                                       self._empty_trashdir_according_criteria)
    def _empty_trashdir_according_criteria(self, info_dir):
        janitor=Janitor(self.date_criteria, self.file_remover)
        janitor.swep(info_dir)
    def println(self, line):
        self.out.write(line + '\n')

class PrintHelp:
    def __init__(self, description, println):
        class Printer:
            def __init__(self, println):
                self.println = println
            def usage(self, usage):
                self.println(usage)
                self.println('')
            def summary(self, summary):
                self.println(summary)
                self.println('')
            def options(self, *line_describing_option):
                self.println('Options:')
                for line in line_describing_option:
                    self.println(line)
                self.println('')
            def bug_reporting(self):
                self.println("Report bugs to http://code.google.com/p/trash-cli/issues")
        self.description  = description
        self.printer      = Printer(println)

    def __call__(self, program_name):
        self.description(program_name, self.printer)

class PrintVersion:
    def __init__(self, println, version):
        self.println      = println
        self.version      = version
    def __call__(self, program_name):
        self.println("%s %s" % (program_name, self.version))

class Janitor:
    def __init__(self, date_criteria, file_remover):
        self.date_criteria = date_criteria
        self.file_remover = file_remover
    def swep(self, infodir):
        infodir.for_all_files_satisfying(self.date_criteria,
                self.remove_trash)
        infodir.for_all_orphans(self.remove_file)
    def remove_file(self, path):
        self.file_remover.remove_file(path)
    def remove_trash(self, trash):
        self.file_remover.remove_file_if_exists(trash.path_to_backup_copy())
        self.file_remover.remove_file(trash.path_to_trashinfo())

def curry_add_info(on_info_dir):
    def on_trash_dir(trash_dir, volume):
        import os
        info_dir = os.path.join(trash_dir, 'info')
        on_info_dir(info_dir, volume)
    return on_trash_dir

class AvailableTrashDir:
    def __init__(self, environ, getuid, list_volumes, 
                 is_sticky_dir= lambda path: True):
        self.environ       = environ
        self.getuid        = getuid
        self.list_volumes  = list_volumes
        self.is_sticky_dir = is_sticky_dir
    def for_each_infodir(self, file_reader, action):
        def action2(info_dir_path, volume_path):
            infodir = InfoDir(file_reader, info_dir_path, volume_path)
            action(infodir)
        self.for_home_trashcan(curry_add_info(action2))
        self.for_each_volume_trashcans(curry_add_info(action2))
    def for_each_infodir_and_volume(self, action):
        self.for_home_trashcan(action)
        self.for_each_volume_trashcans(action)
    def for_home_trashcan(self, action):
        if 'XDG_DATA_HOME' in self.environ:
            action('%(XDG_DATA_HOME)s/Trash' % self.environ, '/')
        elif 'HOME' in self.environ:
            action('%(HOME)s/.local/share/Trash' % self.environ, '/')
    def for_each_volume_trashcans(self, action):
        from os.path import join
        for volume in self.list_volumes():
            top_trash_dir = join(volume, '.Trash')
            if self.is_sticky_dir(top_trash_dir):
                action(join(top_trash_dir, str(self.getuid())), volume)
            
            action(join(volume, '.Trash-%s' % self.getuid()), volume)

def always(deletion_date): return True
class OlderThan:
    def __init__(self, days_ago, now):
        from datetime import timedelta
        self.limit_date = now() - timedelta(days=days_ago)
    def __call__(self, deletion_date):
        return deletion_date < self.limit_date

class FilterByDateCriteria:
    def __init__(self, date_criteria, action):
        self.date_criteria = date_criteria
        self.action        = action
    def __call__(self, trashinfo, parsed):
        if self.date_criteria(parsed.deletion_date()):
            self.action(trashinfo)
class InfoDir:
    def __init__(self, file_reader, path, volume_path):
        self.path        = path
        self.file_reader = file_reader
        self.volume_path = volume_path
    def for_all_orphans(self, action):
        for entry in self._files():
            trashinfo_path = self._trashinfo_path_from_file(entry)
            file_path = os.path.join(self._files_dir(), entry)
            if not self.file_reader.exists(trashinfo_path): action(file_path)
    def _files(self):
        return self._entries_if_dir_exists(self._files_dir())
    def _entries_if_dir_exists(self, path):
        return self.file_reader.entries_if_dir_exists(path)
    def for_all_files_satisfying(self, date_criteria, action):
        self.each_trashinfo_lazily_parsed(
                FilterByDateCriteria(date_criteria, action))

    def each_trashinfo_lazily_parsed(self, action):
        for trashinfo in self._trashinfos():

            file_being_parsed = trashinfo.path_to_trashinfo()
            def contents(): return self.file_reader.contents_of(file_being_parsed)
            parser = LazyTrashInfoParser(contents, self.volume_path) 

            action(trashinfo, parser)

    def each_parsed_trashinfo(self, on_parse, on_read_error, on_parse_error):
        class WakingUpParser:
            def __call__(self, trashinfo, parser):
                try:
                    maybe_deletion_date = maybe_date(parser.deletion_date)
                    original_location   = parser.original_location()
                except ParseError, e:
                    on_parse_error(trashinfo.path_to_trashinfo(), e.message)
                except IOError, e:
                    on_read_error(e)
                else:
                    on_parse(maybe_deletion_date, original_location)
        
        self.each_trashinfo_lazily_parsed(WakingUpParser())
            
    def _trashinfos(self):
        for entry in self._trashinfo_entries():
            yield self._trashinfo(entry)
    def _trashinfo(self, entry):
        class TrashInfo:
            def __init__(self, info_dir, files_dir, entry, file_reader,
                         volume_path):
                self.info_dir    = info_dir      
                self.files_dir   = files_dir     
                self.entry       = entry         
            def path_to_backup_copy(self):
                entry = self.entry[:-len('.trashinfo')]
                return os.path.join(self.files_dir, entry)
            def path_to_trashinfo(self):
                return os.path.join(self.info_dir, self.entry)
        return TrashInfo(self.path, 
                         self._files_dir(), 
                         entry, 
                         self.file_reader, 
                         self.volume_path)
    def _trashinfo_path_from_file(self, file_entry):
        return os.path.join(self.path, file_entry + '.trashinfo')
    def _files_dir(self):
        return os.path.join(os.path.dirname(self.path), 'files')
    def _trashinfo_entries(self):
        for entry in self._entries_if_dir_exists(self.path):
            if entry.endswith('.trashinfo'):
                yield entry
    def _trashinfo_path(self, entry):
        return os.path.join(self.path, entry)

class ParseError(ValueError): pass

class LazyTrashInfoParser:
    def __init__(self, contents, volume_path):
        self.contents    = contents
        self.volume_path = volume_path
    def deletion_date(self):
        return parse_deletion_date(self.contents())
    def _path(self):
        return parse_path(self.contents())
    def original_location(self):
        return os.path.join(self.volume_path, self._path())

def maybe_parse_deletion_date(contents):
    return maybe_date(lambda:parse_deletion_date(contents))

def maybe_date(parsing_closure):
    try:
        date = parsing_closure()
    except ValueError:
        return unknown_date()
    else:
        if date: return date
    return unknown_date()

def unknown_date():
    return '????-??-?? ??:??:??'

def parse_deletion_date(contents):
    from datetime import datetime 
    for line in contents.split('\n'):
        if line.startswith('DeletionDate='):
            return datetime.strptime(line, "DeletionDate=%Y-%m-%dT%H:%M:%S")
def parse_path(contents):
    import urllib
    for line in contents.split('\n'):
        if line.startswith('Path='):
            return urllib.unquote(line[len('Path='):])
    raise ParseError('Unable to parse Path')

def has_sticky_bit(path):
    import os
    import stat
    return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX

