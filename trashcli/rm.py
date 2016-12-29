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
            self.stderr.write('Usage:\n'
                              '    trash-rm PATTERN\n'
                              '\n'
                              'Please specify PATTERN\n')
            self.exit_code = 8
            return

        def unable_to_parse_path(trashinfo):
            self.stderr.write('trash-rm: {}: unable to parse \'Path\'\n'.format(
                    trashinfo))

        trashcan = CleanableTrashcan(FileRemover())
        cmd = Filter(trashcan.delete_trashinfo_and_backup_copy)
        cmd.use_pattern(args[0])
        listing = ListTrashinfos(cmd.delete_if_matches, self.file_reader)
        listing.unable_to_parse_path = unable_to_parse_path
        top_trashdir_rules = TopTrashDirRules(self.file_reader)
        trashdirs   = TrashDirs(self.environ, self.getuid,
                                list_volumes = self.list_volumes,
                                top_trashdir_rules = top_trashdir_rules)
        trashdirs.on_trash_dir_found = listing.list_from_volume_trashdir

        trashdirs.list_trashdirs()

def main():
    from trashcli.list_mount_points import mount_points
    main = RmCmd(environ        = os.environ
                 , getuid       = os.getuid
                 , list_volumes = mount_points
                 , stderr       = sys.stderr
                 , file_reader  = FileSystemReader())

    main.run(sys.argv)

    return main.exit_code

class Filter:
    def __init__(self, trashcan):
        self.delete = trashcan
    def use_pattern(self, pattern):
        self.pattern = pattern
    def delete_if_matches(self, original_location, info_file):
        basename = os.path.basename(original_location)
        if fnmatch.fnmatchcase(basename, self.pattern):
            self.delete(info_file)

class ListTrashinfos:
    def __init__(self, out, file_reader):
        self.out = out
        self.file_reader = file_reader
    def list_from_home_trashdir(self, trashdir_path):
        self.list_from_volume_trashdir(trashdir_path, '/')
    def list_from_volume_trashdir(self, trashdir_path, volume):
        self.volume = volume
        self.trashdir = TrashDir(self.file_reader)
        self.trashdir.open(trashdir_path, volume)
        self.trashdir.each_trashinfo(self._report_original_location)
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
