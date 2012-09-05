from mock import Mock

from files import write_file, require_empty_dir

from trashcli.fs    import FileSystemReader
from trashcli.trash import TrashDirs, Harvester
from trashcli.trash import parse_path
from trashcli.trash import do_nothing
import os

class Listing:
    def __init__(self, environ, getuid, file_reader, mount_points):
        trashdirs        = TrashDirs(environ, getuid, file_reader, mount_points)
        self.harvester   = Harvester(trashdirs, file_reader)
        self.contents_of = file_reader.contents_of

        self.found_trash = do_nothing
        self.volume = None

    def search(self):
        self.harvester.on_trashinfo_found = self._report
        self.harvester.search()
    def _report(self, trashinfo_path):
        trashinfo     = self.contents_of(trashinfo_path)
        original_path = parse_path(trashinfo)
        abs_orig_path = os.path.join(self.volume, original_path)
        self.found_trash(abs_orig_path , trashinfo_path)

class Test_list_all_original_path_with_trashinfo:
    def test(self):
        self.out = Mock()
        require_empty_dir('xdh')
        self.listing = Listing( environ      = {'XDG_DATA_HOME':'xdh'},
                           getuid       = lambda: 123,
                           file_reader  = FileSystemReader(),
                           mount_points = lambda:[])

        self.add_trashinfo('xdh/Trash/info/cippa.trashinfo', '/cippa')
        self.listing.found_trash = self.out
        self.listing.search()

        self.out.assert_called_with('/cippa',
                                       'xdh/Trash/info/cippa.trashinfo')

    def add_trashinfo(self, trashinfo_path, trashed_file_original_path):
        write_file(trashinfo_path, "[Trash Info]\n"
                                   "Path=%s\n" % trashed_file_original_path)


