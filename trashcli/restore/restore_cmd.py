# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import TextIO, Callable, MutableMapping

from trashcli.fstab.volumes import Volumes
from trashcli.lib.my_input import Input
from trashcli.lib.print_version import PrintVersionAction, PrintVersionArgs
from trashcli.restore.args import RunRestoreArgs
from trashcli.restore.file_system import RestoreReadFileSystem, \
    RestoreWriteFileSystem, ReadCwd, ListingFileSystem, FileReader
from trashcli.restore.handler import HandlerImpl
from trashcli.restore.info_dir_searcher import InfoDirSearcher
from trashcli.restore.info_files import InfoFiles
from trashcli.restore.real_output import RealOutput
from trashcli.restore.restore_arg_parser import RestoreArgParser
from trashcli.restore.restore_logger import RestoreLogger
from trashcli.restore.restorer import Restorer
from trashcli.restore.run_restore_action import RunRestoreAction, Handler
from trashcli.restore.trash_directories import TrashDirectoriesImpl
from trashcli.restore.trashed_files import TrashedFiles
from trashcli.trash_dirs_scanner import TopTrashDirRules


class RestoreCmd(object):
    @staticmethod
    def make_from_environment(stdout,  # type: TextIO
                              stderr,  # type: TextIO
                              exit,  # type: Callable[[int], None]
                              input,  # type: Input
                              version,  # type: str
                              listing_file_system,  # type: ListingFileSystem
                              volumes,  # type: Volumes
                              logger,  # type: RestoreLogger
                              uid,  # type: int
                              environ,  # type: MutableMapping[str, str]
                              top_trash_dir_rules_reader,  # type: TopTrashDirRules.Reader
                              file_reader,  # type: FileReader
                              read_fs,   # type: RestoreReadFileSystem
                              write_fs,  # type: RestoreWriteFileSystem
                              read_cwd,  # type: ReadCwd
                              ):
        # build the trash-directory pipeline from environment dependencies here so test and production share the same wiring
        trash_directories = TrashDirectoriesImpl(
            volumes, uid, environ,
            TopTrashDirRules(top_trash_dir_rules_reader),
            logger)
        searcher = InfoDirSearcher(trash_directories,
                                   InfoFiles(listing_file_system))
        trashed_files = TrashedFiles(logger, file_reader, searcher)
        return RestoreCmd.make(stdout, stderr, exit, input, version,
                               trashed_files, read_fs, write_fs, read_cwd)

    @staticmethod
    def make(stdout,  # type: TextIO
             stderr,  # type: TextIO
             exit,  # type: Callable[[int], None]
             input,  # type: Input
             version,  # type: str
             trashed_files,  # type: TrashedFiles
             read_fs,  # type: RestoreReadFileSystem
             write_fs,  # type: RestoreWriteFileSystem
             read_cwd,  # type: ReadCwd
             ):  # type: (...) -> RestoreCmd
        restorer = Restorer(read_fs, write_fs)
        output = RealOutput(stdout, stderr, exit)
        handler = HandlerImpl(input, read_cwd, restorer, output)
        return RestoreCmd(stdout, version, trashed_files, read_cwd, handler)

    def __init__(self,
                 stdout,  # type: TextIO
                 version,  # type: str
                 trashed_files,  # type: TrashedFiles
                 read_cwd,  # type: ReadCwd
                 handler,  # type: Handler
                 ):
        self.read_cwd = read_cwd
        self.parser = RestoreArgParser()
        self.run_restore_action = RunRestoreAction(handler,
                                                   trashed_files)
        self.print_version_action = PrintVersionAction(stdout,
                                                       version)

    def run(self, argv):
        args = self.parser.parse_restore_args(argv,
                                              self.read_cwd.getcwd_as_realpath())

        if isinstance(args, RunRestoreArgs):
            self.run_restore_action.run_action(args)
        elif isinstance(args, PrintVersionArgs):
            self.print_version_action.run_action(args)
