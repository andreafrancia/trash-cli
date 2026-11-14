from typing import NamedTuple, List, Mapping, Callable

from trashcli.empty.clock import Clock
from trashcli.empty.console import Console
from trashcli.empty.delete_according_date import (
    DeleteAccordingDate,
)
from trashcli.empty.emptier import Emptier
from trashcli.empty.empty_fs import EmptyFs
from trashcli.empty.guard import Guard
from trashcli.empty.parse_reply import parse_reply
from trashcli.empty.prepare_output_message import prepare_output_message
from trashcli.empty.user import User
from trashcli.fslib.remove_file_if_exists import RemoveFileIfExists
from trashcli.fslib.protocols.volumes_listing import VolumesListing
from trashcli.fslib.protocols.volume_of import VolumeOfFs
from trashcli.lib.environ import Environ
from trashcli.lib.my_input import RealInput
from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.list.trash_dir_selector import TrashDirsSelector


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
                 volumes_listing,  # type: VolumesListing
                 volumes,  # type: VolumeOfFs
                 console,  # type: Console
                 environ,  # type: Mapping[str, str]
                 geteuid,  # type: Callable[[], int]
                 fs, # type: EmptyFs
                 ):  # type: (...) -> None
        file_remover = RemoveFileIfExists(fs, environ, geteuid)
        self.selector = TrashDirsSelector.make(volumes_listing,
                                               fs,
                                               volumes)
        trash_dir_reader = TrashDirReader(fs)
        delete_mode = DeleteAccordingDate(fs,
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
