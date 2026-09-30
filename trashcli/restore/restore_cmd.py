# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import TextIO, Callable, MutableMapping

from trashcli.fslib.protocols.list_files_in_dir import ListFilesInDir
from trashcli.fstab.volumes import Volumes
from trashcli.lib.my_input import Input
from trashcli.lib.print_version import PrintVersionAction, PrintVersionArgs
from trashcli.put.fs.volume_path_fs import VolumePathFs
from trashcli.restore.args import RunRestoreArgs
from trashcli.restore.fs.protocols.file_reader_fs import FileReaderFs
from trashcli.restore.fs.protocols.path_reader_fs import PathReaderFs
from trashcli.restore.fs.protocols.restore_writer_fs import RestoreWriterFs
from trashcli.restore.fs.protocols.read_cwd_fs import ReadCwdFs
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
from trashcli.trash_dirs_scanner import TopTrashDirRules, TopTrashDirRulesFs


class RestoreCmd(object):
    
    def __init__(self,
                 stdout,  # type: TextIO
                 stderr,  # type: TextIO
                 exit,  # type: Callable[[int], None]
                 input,  # type: Input
                 version,  # type: str
                 listing_fs,  # type: ListFilesInDir
                 volumes,  # type: Volumes
                 logger,  # type: RestoreLogger
                 uid,  # type: int
                 environ,  # type: MutableMapping[str, str]
                 top_trash_dir_rules_fs,  # type: TopTrashDirRulesFs
                 file_reader,  # type: FileReaderFs
                 read_fs,  # type: PathReaderFs
                 write_fs,  # type: RestoreWriterFs
                 read_cwd,  # type: ReadCwdFs
                 volume_path_fs,  # type: VolumePathFs
                 ):  # type: (...) -> None
        # build the trash-directory pipeline from environment dependencies here so test and production share the same wiring
        trash_directories = TrashDirectoriesImpl(
            volumes, uid, environ,
            TopTrashDirRules(top_trash_dir_rules_fs),
            logger)
        searcher = InfoDirSearcher(trash_directories,
                                   InfoFiles(listing_fs))
        trashed_files = TrashedFiles(logger, file_reader, searcher,
                                     volume_path_fs)
        restorer = Restorer(read_fs, write_fs)
        output = RealOutput(stdout, stderr, exit)
        handler = HandlerImpl(input, read_cwd, restorer, output)
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
