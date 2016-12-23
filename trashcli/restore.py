import os
import sys

from .trash import parse_path
from .trash import parse_deletion_date
from .trash import version
from .fstab import Fstab
from .trash import TrashDirectory
from .trash import TrashDirectories
from .fs import contents_of
from .trash import backup_file_path_from

def getcwd_as_realpath(): return os.path.realpath(os.curdir)

class RestoreCmd(object):
    def __init__(self, stdout, stderr, environ, exit, input,
                 curdir = getcwd_as_realpath, version = version):
        self.out      = stdout
        self.err      = stderr
        self.exit     = exit
        self.input    = input
        fstab = Fstab()
        self.mount_points = fstab.mount_points()
        self.trashcan = TrashDirectories(
                volume_of     = fstab.volume_of,
                getuid        = os.getuid,
                environ       = environ)
        self.curdir   = curdir
        self.version = version
    def run(self, args = sys.argv):
        if '--version' in args[1:]:
            command = os.path.basename(args[0])
            self.println('%s %s' %(command, self.version))
            return

        trashed_files = []
        self.for_all_trashed_file_in_dir(trashed_files.append, self.curdir())

        if not trashed_files:
            self.report_no_files_found()
        else :
            for i, trashedfile in enumerate(trashed_files):
                self.println("%4d %s %s" % (i, trashedfile.deletion_date, trashedfile.path))
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
                trashed_files[index].restore()
            except (ValueError, IndexError) as e:
                self.printerr("Invalid entry")
                self.exit(1)
            except IOError as e:
                self.printerr(e)
                self.exit(1)
    def for_all_trashed_file_in_dir(self, action, dir):
        def is_trashed_from_curdir(trashedfile):
            return trashedfile.path.startswith(dir + os.path.sep)
        for trashedfile in filter(is_trashed_from_curdir,
                                  self.all_trashed_files()) :
            action(trashedfile)
    def all_trashed_files(self):
        for trash_dir in all_trash_directories(self.trashcan, self.mount_points):
            for trashedfile in self.trashed_files(trash_dir):
                yield trashedfile
    def trashed_files(self, trash_dir) :
        for info_file in trash_dir.all_info_files():
            try:
                yield self._create_trashed_file_from_info_file(info_file, trash_dir)
            except ValueError:
                trash_dir.logger.warning("Non parsable trashinfo file: %s" % info_file)
            except IOError as e:
                trash_dir.logger.warning(str(e))

    def _create_trashed_file_from_info_file(self, trashinfo_file_path, trash_dir):

        trash_info2 = LazyTrashInfoParser(
                lambda:contents_of(trashinfo_file_path), trash_dir.volume)

        original_location = trash_info2.original_location()
        deletion_date     = trash_info2.deletion_date()
        backup_file_path  = backup_file_path_from(trashinfo_file_path)

        return TrashedFile(original_location, deletion_date,
                trashinfo_file_path, backup_file_path, trash_dir)

    def report_no_files_found(self):
        self.println("No files trashed from current dir ('%s')" % self.curdir())
    def println(self, line):
        self.out.write(line + '\n')
    def printerr(self, msg):
        self.err.write('%s\n' % msg)

def all_trash_directories(trash_directories, mount_points):
    collected = []
    def add_trash_dir(path, volume):
        collected.append(TrashDirectory(path, volume))

    trash_directories.home_trash_dir(add_trash_dir)
    for volume in mount_points:
        trash_directories.volume_trash_dir1(volume, add_trash_dir)
        trash_directories.volume_trash_dir2(volume, add_trash_dir)

    return collected

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

from .fs import move, mkdirs
from .fs import remove_file
import fs
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
    def __init__(self, path, deletion_date, info_file, actual_path,
            trash_directory):
        self.path = path
        self.deletion_date = deletion_date
        self.info_file = info_file
        self.actual_path = actual_path
        self.trash_directory = trash_directory
        self.original_file = actual_path
        self.fs = fs
        self.path_exists = os.path.exists

    def restore(self) :
        if self.path_exists(self.path):
            raise IOError('Refusing to overwrite existing file "%s".' % os.path.basename(self.path))
        else:
            parent = os.path.dirname(self.path)
            self.fs.mkdirs(parent)

        self.fs.move(self.original_file, self.path)
        self.fs.remove_file(self.info_file)
