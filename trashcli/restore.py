import os
import sys

from .list_mount_points import os_mount_points
from .trash import version, home_trash_dir, volume_trash_dir1, volume_trash_dir2
from .fstab import volume_of
from .fs import contents_of, list_files_in_dir
from .trash import backup_file_path_from
from . import fs, trash


class FileSystem:
    def path_exists(self, path):
        return os.path.exists(path)

    def mkdirs(self, path):
        return fs.mkdirs(path)

    def move(self, path, dest):
        return fs.move(path, dest)

    def remove_file(self, path):
        return fs.remove_file(path)

def main():
    try:           # Python 2
        input23 = raw_input
    except:        # Python 3
        input23 = input
    trash_directories = make_trash_directories()
    trashed_files = TrashedFiles(trash_directories, TrashDirectory(),
                                 contents_of)
    RestoreCmd(
        stdout  = sys.stdout,
        stderr  = sys.stderr,
        exit    = sys.exit,
        input   = input23,
        trashed_files=trashed_files,
        mount_points=os_mount_points,
        fs=FileSystem()
    ).run(sys.argv)


def getcwd_as_realpath():
    return os.path.realpath(os.curdir)


def parse_args(sys_argv, curdir):
    import argparse
    parser = argparse.ArgumentParser(
        description='Restores from trash chosen file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('path',
                        default=curdir, nargs='?',
                        help='Restore files from given path instead of current '
                             'directory')
    parser.add_argument('--sort',
                        choices=['date', 'path', 'none'],
                        default='date',
                        help='Sort list of restore candidates by given field')
    parser.add_argument('--trash-dir',
                        action='store',
                        dest='trash_dir',
                        help=argparse.SUPPRESS)
    parser.add_argument('--version', action='store_true', default=False)
    return parser.parse_args(sys_argv[1:])


class TrashedFiles:
    def __init__(self, trash_directories, trash_directory, contents_of):
        self.trash_directories = trash_directories
        self.trash_directory = trash_directory
        self.contents_of = contents_of

    def all_trashed_files(self, volumes, trash_dir_from_cli):
        logger = trash.logger
        for path, volume in self.trash_directories.trash_directories_or_user(
                volumes, trash_dir_from_cli):
            for type, info_file in self.trash_directory.all_info_files(path):
                if type == 'non_trashinfo':
                    logger.warning("Non .trashinfo file in info dir")
                elif type == 'trashinfo':
                    try:
                        trash_info = TrashInfoParser(self.contents_of(info_file),
                                                     volume)
                        original_location = trash_info.original_location()
                        deletion_date     = trash_info.deletion_date()
                        backup_file_path  = backup_file_path_from(info_file)
                        trashedfile = TrashedFile(original_location,
                                                  deletion_date,
                                                  info_file,
                                                  backup_file_path)
                        yield trashedfile
                    except ValueError:
                        logger.warning("Non parsable trashinfo file: %s" % info_file)
                    except IOError as e:
                        logger.warning(str(e))
                else:
                    logger.error("Unexpected file type: %s: %s",
                                 type, info_file)


class RestoreAskingTheUser(object):
    def __init__(self, input, println, restore, die):
        self.input = input
        self.println = println
        self.restore = restore
        self.die = die

    def restore_asking_the_user(self, trashed_files):
        try:
            index = self.input("What file to restore [0..%d]: " % (len(trashed_files) - 1))
        except KeyboardInterrupt:
            return self.die("")
        if index == "":
            self.println("Exiting")
        else:
            try:
                indexes = index.split(',')
                indexes.sort(reverse=True)  # restore largest index first
                for index in indexes:
                    index = int(index)
                    if (index < 0 or index >= len(trashed_files)):
                        raise IndexError("Out of range")
                    trashed_file = trashed_files[index]
                    self.restore(trashed_file)
            except (ValueError, IndexError) as e:
                self.die("Invalid entry")
            except IOError as e:
                self.die(e)


class Restorer(object):
    def __init__(self, fs):
        self.fs = fs

    def restore_trashed_file(self, trashed_file):
        restore(trashed_file, self.fs)

class RestoreCmd(object):
    def __init__(self, stdout, stderr, exit, input,
                 curdir = getcwd_as_realpath, version = version,
                 trashed_files=None, mount_points=None, fs=None):
        self.out      = stdout
        self.err      = stderr
        self.exit     = exit
        self.input    = input
        self.curdir   = curdir
        self.version = version
        self.fs = fs
        self.trashed_files = trashed_files
        self.mount_points = mount_points
    def run(self, argv):
        args = parse_args(argv, self.curdir() + os.path.sep)
        trash_dir_from_cli = args.trash_dir
        if args.version:
            command = os.path.basename(argv[0])
            self.println('%s %s' % (command, self.version))
            return
        trashed_files = list(self.all_files_trashed_from_path(
            args.path, trash_dir_from_cli))
        if args.sort == 'path':
            trashed_files = sorted(trashed_files, key=lambda x: x.original_location + str(x.deletion_date))
        elif args.sort == 'date':
            trashed_files = sorted(trashed_files, key=lambda x: x.deletion_date)
        self.handle_trashed_files(trashed_files)

    def handle_trashed_files(self,trashed_files):
        if not trashed_files:
            self.report_no_files_found()
        else :
            for i, trashedfile in enumerate(trashed_files):
                self.println("%4d %s %s" % (i, trashedfile.deletion_date, trashedfile.original_location))
            self.restore_asking_the_user(trashed_files)
    def restore_asking_the_user(self, trashed_files):
        restore_asking_the_user = RestoreAskingTheUser(self.input,
                                                       self.println,
                                                       self.restore,
                                                       self.die)
        restore_asking_the_user.restore_asking_the_user(trashed_files)

    def die(self, error):
        self.printerr(error)
        self.exit(1)

    def restore(self, trashed_file):
        restorer = Restorer(self.fs)
        restorer.restore_trashed_file(trashed_file)

    def all_files_trashed_from_path(self, path, trash_dir_from_cli):
        def is_trashed_from_curdir(trashed_file):
            return trashed_file.original_location.startswith(path)
        for trashed_file in self.trashed_files.all_trashed_files(
                self.mount_points(), trash_dir_from_cli):
            if is_trashed_from_curdir(trashed_file):
                yield trashed_file

    def report_no_files_found(self):
        self.println("No files trashed from current dir ('%s')" % self.curdir())
    def println(self, line):
        self.out.write(line + '\n')
    def printerr(self, msg):
        self.err.write('%s\n' % msg)

def parse_additional_volumes(volume_from_args):
    if not volume_from_args:
        return []
    return volume_from_args

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


class TrashDirectories2:
    def __init__(self, volume_of, trash_directories):
        self.volume_of = volume_of
        self.trash_directories = trash_directories

    def trash_directories_or_user(self, volumes, trash_dir_from_cli):
        if trash_dir_from_cli:
            return [(trash_dir_from_cli, self.volume_of(trash_dir_from_cli))]
        return self.trash_directories.all_trash_directories(volumes)


def make_trash_directories():
    trash_directories = TrashDirectories(volume_of, os.getuid, os.environ)
    return TrashDirectories2(volume_of, trash_directories)


class TrashDirectories:
    def __init__(self, volume_of, getuid, environ):
        self.volume_of    = volume_of
        self.getuid       = getuid
        self.environ      = environ

    def all_trash_directories(self, volumes):
        for path1, volume1 in home_trash_dir(self.environ, self.volume_of):
            yield path1, volume1
        for volume in volumes:
            for path1, volume1 in volume_trash_dir1(volume, self.getuid):
                yield path1, volume1
            for path1, volume1 in volume_trash_dir2(volume, self.getuid):
                yield path1, volume1

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


def restore(trashed_file, fs):
    if fs.path_exists(trashed_file.original_location):
        raise IOError('Refusing to overwrite existing file "%s".' % os.path.basename(trashed_file.original_location))
    else:
        parent = os.path.dirname(trashed_file.original_location)
        fs.mkdirs(parent)

    fs.move(trashed_file.original_file, trashed_file.original_location)
    fs.remove_file(trashed_file.info_file)


class TrashDirectory:

    def all_info_files(self, path) :
        norm_path = os.path.normpath(path)
        info_dir = os.path.join(norm_path, 'info')
        try :
            for info_file in list_files_in_dir(info_dir):
                if not os.path.basename(info_file).endswith('.trashinfo') :
                    yield ('non_trashinfo', info_file)
                else :
                    yield ('trashinfo', info_file)
        except OSError: # when directory does not exist
            pass
