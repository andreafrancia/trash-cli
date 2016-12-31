import fnmatch
import os, sys

from trashcli.trash import TrashDir, parse_path, ParseError
from trashcli.trash import TrashDirs
from trashcli.trash import TopTrashDirRules
from trashcli.trash import CleanableTrashcan
from trashcli.fs import FileSystemReader
from trashcli.fs import FileRemover

class RmCmd:
    def __init__(self,
                 environ,
                 getuid,
                 list_volumes,
                 stderr,
                 file_reader):
        self.environ      = environ
        self.getuid       = getuid
        self.list_volumes = list_volumes
        self.stderr       = stderr
        self.file_reader  = file_reader
    def run(self, argv):
        args = argv[1:]
        self.exit_code = 0

        if not args:
            self.print_err('Usage:\n'
                           '    trash-rm PATTERN\n'
                           '\n'
                           'Please specify PATTERN')
            self.exit_code = 8
            return

        trashcan = CleanableTrashcan(FileRemover())
        cmd = Filter(trashcan.delete_trashinfo_and_backup_copy)
        cmd.use_pattern(args[0])

        listing = ListTrashinfos(cmd.delete_if_matches,
                                 self.file_reader,
                                 self.unable_to_parse_path)

        trashdirs = TrashDirs(self.environ,
                              self.getuid,
                              self.list_volumes,
                              TopTrashDirRules(self.file_reader))
        trashdirs.on_trash_dir_found = listing.list_from_volume_trashdir

        trashdirs.list_trashdirs()

    def unable_to_parse_path(self, trashinfo):
        self.report_error('{}: unable to parse \'Path\''.format(trashinfo))

    def report_error(self, error_msg):
        self.print_err('trash-rm: {}'.format(error_msg))

    def print_err(self, msg):
        self.stderr.write(msg + '\n')


def main():
    from trashcli.list_mount_points import mount_points
    cmd = RmCmd(environ        = os.environ
                , getuid       = os.getuid
                , list_volumes = mount_points
                , stderr       = sys.stderr
                , file_reader  = FileSystemReader())

    cmd.run(sys.argv)

    return cmd.exit_code

class Filter:
    def __init__(self, delete):
        self.delete = delete
    def use_pattern(self, pattern):
        self.pattern = pattern
    def delete_if_matches(self, original_location, info_file):
        if self.pattern[0] == '/':
            if self.pattern == original_location:
                self.delete(info_file)
        else:
            basename = os.path.basename(original_location)
            if fnmatch.fnmatchcase(basename, self.pattern):
                self.delete(info_file)

class ListTrashinfos:
    def __init__(self, out, file_reader, unable_to_parse_path):
        self.out = out
        self.file_reader = file_reader
        self.unable_to_parse_path = unable_to_parse_path
    def list_from_volume_trashdir(self, trashdir_path, volume):
        self.volume = volume
        trashdir = TrashDir(self.file_reader)
        trashdir.open(trashdir_path, volume)
        trashdir.each_trashinfo(self._report_original_location)
    def _report_original_location(self, trashinfo_path):
        trashinfo = self.file_reader.contents_of(trashinfo_path)
        try:
            path = parse_path(trashinfo)
        except ParseError:
            self.unable_to_parse_path(trashinfo_path)
        else:
            complete_path = os.path.join(self.volume, path)
            self.out(complete_path, trashinfo_path)


if __name__ == '__main__':
    sys.exit(main())
