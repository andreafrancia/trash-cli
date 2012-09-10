import os, sys

class Main:
    def run(self, argv):
        self.exit_code = 0
        from trashcli.trash             import FileSystemReader, TrashDirs, Harvester
        from trashcli.trash             import TopTrashDirRules
        environ     = self.environ
        getuid      = self.getuid
        file_reader = FileSystemReader()
        top_trashdir_rules = TopTrashDirRules(file_reader)
        trashdirs   = TrashDirs(environ, getuid,
                                list_volumes = self.list_volumes,
                                top_trashdir_rules = top_trashdir_rules)
        harvester   = Harvester(file_reader)
        trashdirs.on_trash_dir_found = harvester._analize_trash_directory
        harvester.on_volume = self.set_volume
        harvester.on_trashinfo_found = self.clean_if_matches

        if not argv[1:]:
            self.stderr.write('Usage:\n'
                            '    trash-rm PATTERN\n'
                            '\n'
                            'Please specify PATTERN')
            self.exit_code = 8
            return
    def set_volume(self, volume):
        self.volume = volume

    def clean_if_matches(self, trashinfo_path):
        from trashcli.trash import parse_path
        contents = file(trashinfo_path).read()
        path = parse_path(contents)
        complete_path = os.path.join(self.volume, path)

def main():
    from trashcli.list_mount_points import mount_points
    main              = Main()
    main.environ      = os.environ
    main.getuid       = os.getuid
    main.list_volumes = mount_points
    main.stderr       = sys.stderr

    main.run(sys.argv)

    return main.exit_code

class TrashRmCmd:
    def __init__(self, trash_contents, trashcan):
        self.trash_contents = trash_contents
        self.delete = TrashCanCleaner(trashcan)
    def clean_up_matching(self, pattern):
        self.filter = Pattern(pattern, self.delete)
        self.trash_contents.list_files_to(self.filter)

import fnmatch
class Pattern:
    def __init__(self, pattern, delete):
        self.delete = delete
        self.pattern = pattern
    def garbage(self, original_path, info):
        basename = os.path.basename(original_path)
        if fnmatch.fnmatchcase(basename, self.pattern):
            self.delete.garbage(original_path, info)

class TrashCanCleaner:
    def __init__(self, trashcan):
        self.trashcan = trashcan
    def garbage(self, original_path, info_file, backup_copy=None):
        self.trashcan.release(info_file)

if __name__ == '__main__':
    sys.exit(main())
