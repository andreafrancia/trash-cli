import os

from trashcli.restore.restore_asking_the_user import RestoreAskingTheUser
from trashcli.restore.parse_restore_args import Command, parse_restore_args
from trashcli.trash import version, print_version


class Restorer(object):
    def __init__(self, fs):
        self.fs = fs

    def restore_trashed_file(self, trashed_file, overwrite=False):
        """
        If overwrite is enabled, then the restore functionality will overwrite an existing file
        """
        restore(trashed_file, self.fs, overwrite)


def original_location_matches_path(trashed_file_original_location, path):
    if path == os.path.sep:
        return True
    if trashed_file_original_location.startswith(path + os.path.sep):
        return True
    return trashed_file_original_location == path


class RestoreCmd(object):
    def __init__(self, stdout, stderr, exit, input, version=version,
                 trashed_files=None, mount_points=None, fs=None):
        self.out = stdout
        self.err = stderr
        self.exit = exit
        self.input = input
        self.version = version
        self.fs = fs
        self.trashed_files = trashed_files
        self.mount_points = mount_points

    def run(self, argv):
        cmd, args = parse_restore_args(argv, self.fs.getcwd_as_realpath())
        if cmd == Command.PrintVersion:
            command = os.path.basename(argv[0])
            print_version(self.out, command, self.version)
            return
        elif cmd == Command.RunRestore:
            trash_dir_from_cli = args['trash_dir']
            trashed_files = list(self.all_files_trashed_from_path(
                args['path'], trash_dir_from_cli))
            if args['sort'] == 'path':
                trashed_files = sorted(trashed_files,
                                       key=lambda x: x.original_location + str(
                                           x.deletion_date))
            elif args['sort'] == 'date':
                trashed_files = sorted(trashed_files,
                                       key=lambda x: x.deletion_date)

            self.handle_trashed_files(trashed_files, args['overwrite'])

    def handle_trashed_files(self, trashed_files, overwrite=False):
        if not trashed_files:
            self.report_no_files_found()
        else:
            for i, trashedfile in enumerate(trashed_files):
                self.println("%4d %s %s" % (i,
                                            trashedfile.deletion_date,
                                            trashedfile.original_location))
            self.restore_asking_the_user(trashed_files, overwrite)

    def restore_asking_the_user(self, trashed_files, overwrite=False):
        restore_asking_the_user = RestoreAskingTheUser(self.input,
                                                       self.println,
                                                       self.restore,
                                                       self.die)
        restore_asking_the_user.restore_asking_the_user(trashed_files,
                                                        overwrite)

    def die(self, error):
        self.printerr(error)
        self.exit(1)

    def restore(self, trashed_file, overwrite=False):
        restorer = Restorer(self.fs)
        restorer.restore_trashed_file(trashed_file, overwrite)

    def all_files_trashed_from_path(self, path, trash_dir_from_cli):
        for trashed_file in self.trashed_files.all_trashed_files(
                self.mount_points(), trash_dir_from_cli):
            if original_location_matches_path(trashed_file.original_location,
                                              path):
                yield trashed_file

    def report_no_files_found(self):
        self.println("No files trashed from current dir ('%s')" % self.fs.getcwd_as_realpath())

    def println(self, line):
        self.out.write(line + '\n')

    def printerr(self, msg):
        self.err.write('%s\n' % msg)


def restore(trashed_file, fs, overwrite=False):
    if not overwrite and fs.path_exists(trashed_file.original_location):
        raise IOError(
            'Refusing to overwrite existing file "%s".' % os.path.basename(
                trashed_file.original_location))
    else:
        parent = os.path.dirname(trashed_file.original_location)
        fs.mkdirs(parent)

    fs.move(trashed_file.original_file, trashed_file.original_location)
    fs.remove_file(trashed_file.info_file)
