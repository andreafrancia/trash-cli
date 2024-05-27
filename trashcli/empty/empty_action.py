from typing import List
from typing import NamedTuple

from trashcli.empty.clock import Clock
from trashcli.empty.console import Console
from trashcli.empty.delete_according_date import (
    DeleteAccordingDate,
)
from trashcli.empty.emptier import Emptier
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.guard import Guard
from trashcli.empty.parse_reply import parse_reply
from trashcli.empty.prepare_output_message import prepare_output_message
from trashcli.empty.user import User
from trashcli.fs import FileReader
from trashcli.fstab.mount_points_listing import MountPointsListing
from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.dir_reader import DirReader
from trashcli.lib.environ import Environ
from trashcli.lib.my_input import RealInput
from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.list.trash_dir_selector import TrashDirsSelector
from trashcli.trash_dirs_scanner import TopTrashDirRules


class EmptyActionArgs(
    NamedTuple('EmptyActionArgs', [
        ('user_specified_trash_dirs', List[str]),
        ('all_users', bool),
        ('interactive', bool),
        ('days', int),
        ('dry_run', bool),
        ('verbose', int),
        ('environ', Environ),
        ('uid', int),
    ])):
    pass


class EmptyAction:
    def __init__(self,
                 clock,  # type: Clock
                 file_remover,  # type: ExistingFileRemover
                 file_reader,  # type: TopTrashDirRules.Reader
                 volumes,  # type: VolumeOf
                 dir_reader,  # type: DirReader
                 content_reader,  # type: FileReader
                 console,  # type: Console
                 mount_point_listing,  # type: MountPointsListing
                 ):  # type: (...) -> None
        self.selector = TrashDirsSelector.make(file_reader,
                                               volumes,
                                               mount_point_listing)
        trash_dir_reader = TrashDirReader(dir_reader)
        delete_mode = DeleteAccordingDate(content_reader,
                                          clock)
        user = User(prepare_output_message, RealInput(), parse_reply)
        self.emptier = Emptier(delete_mode, trash_dir_reader, file_remover,
                               console)
        self.guard = Guard(user)

    def run_action(self,
                   args,  # type: EmptyActionArgs
                   ):  # type: (...) -> None
        trash_dirs = self.selector.select(args.all_users,
                                          args.user_specified_trash_dirs,
                                          args.environ,
                                          args.uid)
        delete_pass = self.guard.ask_the_user(args.interactive,
                                              trash_dirs)
        if delete_pass.ok_to_empty:
            self.emptier.do_empty(delete_pass.trash_dirs, args.environ,
                                  args.days, args.dry_run, args.verbose)
