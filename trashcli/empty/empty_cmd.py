import os

from trashcli.empty.cleanable_trashcan import CleanableTrashcan
from trashcli.empty.delete_according_date import DeleteAccordingDate
from trashcli.empty.delete_anything import DeleteAnything
from trashcli.empty.emptier import Emptier
from trashcli.empty.errors import Errors
from trashcli.empty.file_remove_with_error_handling import \
    FileRemoveWithErrorHandling
from trashcli.empty.guard import Guard
from trashcli.empty.is_input_interactive import is_input_interactive
from trashcli.empty.main_loop import MainLoop
from trashcli.empty.make_parser import make_parser
from trashcli.empty.no_guard import NoGuard
from trashcli.empty.parse_reply import parse_reply
from trashcli.empty.prepare_output_message import prepare_output_message
from trashcli.empty.user import User
from trashcli.list import TrashDirsSelector
from trashcli.trash import Clock, TrashDirReader, print_version, println, \
    my_input, EX_OK


class EmptyCmd:
    def __init__(self,
                 out,
                 err,
                 environ,
                 volumes_listing,
                 now,
                 file_reader,
                 getuid,
                 file_remover,
                 version,
                 volume_of):
        self.out = out
        self.err = err
        self.file_reader = file_reader
        self.version = version
        self.now = now
        self.uid = getuid()
        self.environ = environ
        file_remover_with_error = FileRemoveWithErrorHandling(file_remover,
                                                              self.print_cannot_remove_error)
        trashcan = CleanableTrashcan(file_remover_with_error)
        self.selector = TrashDirsSelector.make(volumes_listing, file_reader,
                                               volume_of)
        trash_dir_reader = TrashDirReader(self.file_reader)
        self.main_loop = MainLoop(trash_dir_reader, trashcan)

    def run(self, argv, environ):
        clock = Clock(self.now, environ)
        program_name = os.path.basename(argv[0])
        self.errors = Errors(program_name, self.err)
        parser = make_parser(is_input_interactive())
        parsed = parser.parse_args(argv[1:])

        if parsed.version:
            print_version(self.out, program_name, self.version)
        elif parsed.print_time:
            now_value = clock.get_now_value(self.errors)
            println(self.out, now_value.replace(microsecond=0).isoformat())
        else:
            if not parsed.days:
                delete_mode = DeleteAnything()
            else:
                delete_mode = DeleteAccordingDate(self.file_reader.contents_of,
                                                  clock,
                                                  int(parsed.days),
                                                  self.errors)
            trash_dirs = self.selector.select(parsed.all_users,
                                              parsed.user_specified_trash_dirs,
                                              self.environ,
                                              self.uid)
            guard = Guard() if parsed.interactive else NoGuard()
            emptier = Emptier(self.main_loop, delete_mode)

            user = User(prepare_output_message, my_input, parse_reply)
            guard.ask_the_user(user, trash_dirs, emptier)
        return EX_OK

    def print_cannot_remove_error(self, path):
        self.errors.print_error("cannot remove %s" % path)
