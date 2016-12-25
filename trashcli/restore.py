import os
import sys

from .trash import version
from .fstab import Fstab
from .trash import TrashDirectory
from .trash import TrashDirectories
from .fs import contents_of
from .trash import backup_file_path_from
import fs

def getcwd_as_realpath(): return os.path.realpath(os.curdir)

class RestoreCmd(object):
    def __init__(self, stdout, stderr, environ, exit, input,
                 curdir = getcwd_as_realpath, version = version):
        self.out      = stdout
        self.err      = stderr
        self.exit     = exit
        self.input    = input
        self.curdir   = curdir
        self.version = version
        self.fs = fs
        self.path_exists = os.path.exists
        self.contents_of = contents_of
        fstab = Fstab()
        all_trash_directories = AllTrashDirectories(
                volume_of    = fstab.volume_of,
                getuid       = os.getuid,
                environ      = environ,
                mount_points = fstab.mount_points()
                )
        self.all_trash_directories2 = all_trash_directories.all_trash_directories
    def run(self, argv):
        if '--version' in argv[1:]:
            command = os.path.basename(argv[0])
            self.println('%s %s' %(command, self.version))
            return
        if len(argv) == 2:
            specific_path = argv[1]
            def is_trashed_from_curdir(trashedfile):
                return trashedfile.original_location.startswith(specific_path)
            filter = is_trashed_from_curdir
        else:
            dir = self.curdir()
            def is_trashed_from_curdir(trashedfile):
                return trashedfile.original_location.startswith(dir + os.path.sep)
            filter = is_trashed_from_curdir
        trashed_files = self.all_trashed_files_filter(filter)
        self.handle_trashed_files(trashed_files)

    def handle_trashed_files(self,trashed_files):
        if not trashed_files:
            self.report_no_files_found()
        else :
            for i, trashedfile in enumerate(trashed_files):
                self.println("%4d %s %s" % (i, trashedfile.deletion_date, trashedfile.original_location))
            self.restore_asking_the_user(trashed_files)
    def restore_asking_the_user(self, trashed_files):
        index=self.input("What file to restore [0..%d]: " % (len(trashed_files)-1))
        if index == "" :
            self.println("Exiting")
        else :
            try:
                index = int(index)
                if (index < 0 or index >= len(trashed_files)):
                    raise IndexError("Out of range")
                trashed_file = trashed_files[index]
                self.restore(trashed_file)
            except (ValueError, IndexError) as e:
                self.printerr("Invalid entry")
                self.exit(1)
            except IOError as e:
                self.printerr(e)
                self.exit(1)
    def restore(self, trashed_file):
        restore(trashed_file, self.path_exists, self.fs)
    def all_trashed_files_filter(self, matches):
        trashed_files = []
        for trashedfile in self.all_trashed_files():
            if matches(trashedfile):
                trashed_files.append(trashedfile)
        return trashed_files
    def all_trashed_files(self):
        for trash_dir in self.all_trash_directories2():
            for info_file in trash_dir.all_info_files():
                try:
                    trash_info = TrashInfoParser(self.contents_of(info_file),
                                                 trash_dir.volume)
                    original_location = trash_info.original_location()
                    deletion_date     = trash_info.deletion_date()
                    backup_file_path  = backup_file_path_from(info_file)
                    trashedfile = TrashedFile(original_location,
                                              deletion_date,
                                              info_file,
                                              backup_file_path)
                    yield trashedfile
                except ValueError:
                    trash_dir.logger.warning("Non parsable trashinfo file: %s" % info_file)
                except IOError as e:
                    trash_dir.logger.warning(str(e))
    def report_no_files_found(self):
        self.println("No files trashed from current dir ('%s')" % self.curdir())
    def println(self, line):
        self.out.write(line + '\n')
    def printerr(self, msg):
        self.err.write('%s\n' % msg)

from .trash import parse_path
from .trash import parse_deletion_date
class TrashInfoParser:
    def __init__(self, contents, volume_path):
        self.contents    = contents
        self.volume_path = volume_path
    def deletion_date(self):
        return parse_deletion_date(self.contents)
    def original_location(self):
        path = parse_path(self.contents)
        return os.path.join(self.volume_path, path)

class AllTrashDirectories:
    def __init__(self, volume_of, getuid, environ, mount_points):
        self.volume_of    = volume_of
        self.getuid       = getuid
        self.environ      = environ
        self.mount_points = mount_points
    def all_trash_directories(self):
        trash_directories = TrashDirectories(volume_of = self.volume_of,
                                             getuid    = self.getuid,
                                             environ   = self.environ)
        collected = []
        def add_trash_dir(path, volume):
            collected.append(TrashDirectory(path, volume))

        trash_directories.home_trash_dir(add_trash_dir)
        for volume in self.mount_points:
            trash_directories.volume_trash_dir1(volume, add_trash_dir)
            trash_directories.volume_trash_dir2(volume, add_trash_dir)

        return collected

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
     - original_file : the path where the trashed file has been placed after the
                       trash opeartion (instance of Path)
    """
    def __init__(self, original_location,
                       deletion_date,
                       info_file,
                       original_file):
        self.original_location = original_location
        self.deletion_date = deletion_date
        self.info_file = info_file
        self.original_file = original_file

def restore(trashed_file, path_exists, fs):
    if path_exists(trashed_file.original_location):
        raise IOError('Refusing to overwrite existing file "%s".' % os.path.basename(trashed_file.original_location))
    else:
        parent = os.path.dirname(trashed_file.original_location)
        fs.mkdirs(parent)

    fs.move(trashed_file.original_file, trashed_file.original_location)
    fs.remove_file(trashed_file.info_file)

