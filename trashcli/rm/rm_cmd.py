# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
from trashcli.compat import Protocol

from trashcli.fs import ContentsOf
from trashcli.lib.dir_checker import DirChecker
from trashcli.lib.dir_reader import DirReader
from trashcli.lib.user_info import SingleUserInfoProvider
from trashcli.rm.cleanable_trashcan import CleanableTrashcan
from trashcli.rm.file_remover import FileRemover
from trashcli.rm.filter import Filter
from trashcli.rm.list_trashinfo import ListTrashinfos
from trashcli.trash_dirs_scanner import TrashDirsScanner, TopTrashDirRules, \
    trash_dir_found


class RmFileSystemReader(ContentsOf,
                         DirReader,
                         TopTrashDirRules.Reader,
                         Protocol):
    pass


class RmCmd:
    def __init__(self,
                 environ,
                 getuid,
                 volumes_listing,
                 stderr,
                 file_reader,  # type: RmFileSystemReader
                 ):
        self.environ = environ
        self.getuid = getuid
        self.volumes_listing = volumes_listing
        self.stderr = stderr
        self.file_reader = file_reader

    def run(self, argv, uid):
        args = argv[1:]
        self.exit_code = 0

        if not args:
            self.print_err('Usage:\n'
                           '    trash-rm PATTERN\n'
                           '\n'
                           'Please specify PATTERN.\n'
                           'trash-rm uses fnmatch.fnmatchcase to match patterns, see https://docs.python.org/3/library/fnmatch.html for more details.')
            self.exit_code = 8
            return

        trashcan = CleanableTrashcan(FileRemover())
        cmd = Filter(args[0])

        listing = ListTrashinfos.make(self.file_reader, self.file_reader)

        user_info_provider = SingleUserInfoProvider()
        scanner = TrashDirsScanner(user_info_provider,
                                   self.volumes_listing,
                                   TopTrashDirRules(self.file_reader),
                                   DirChecker())

        for event, args in scanner.scan_trash_dirs(self.environ, uid):
            if event == trash_dir_found:
                path, volume = args
                for type, arg in listing.list_from_volume_trashdir(path,
                                                                   volume):
                    if type == 'unable_to_parse_path':
                        self.unable_to_parse_path(arg)
                    elif type == 'trashed_file':
                        original_location, info_file = arg
                        if cmd.matches(original_location):
                            trashcan.delete_trash_info_and_backup_copy(
                                info_file)

    def unable_to_parse_path(self, trashinfo):
        self.report_error('{}: unable to parse \'Path\''.format(trashinfo))

    def report_error(self, error_msg):
        self.print_err('trash-rm: {}'.format(error_msg))

    def print_err(self, msg):
        self.stderr.write(msg + '\n')
