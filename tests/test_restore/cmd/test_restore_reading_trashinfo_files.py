from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.restore_user import RestoreUser
from tests.support.trash_dirs.given_trash import \
    GivenTrash
from tests.test_restore.support.recording_logger import RecordingLogger


# How trash-restore turns each entry of the info dirs into either a file
# offered for restore or a warning.
# These tests were previously unit tests of TrashedFiles (see commit
# c4a2c055 for their documented purpose), now rewritten against the command.
class TestRestoreReadingTrashinfoFiles:
    def setup_method(self):
        self.fs = FakeFs()
        self.log_messages = []
        self.user = RestoreUser(environ={'HOME': '/home/user'},
                                uid=123,
                                file_reader=self.fs,
                                path_read_fs=self.fs,
                                write_fs=self.fs,
                                listing_fs=self.fs,
                                version='1.0',
                                volumes=self.fs,
                                volume_path_fs=self.fs,
                                top_trash_dir_rules_reader=self.fs,
                                logger=RecordingLogger(self.log_messages))
        self.home_trash = '/home/user/.local/share/Trash'
        self.volume_trash = '/volume/.Trash-123'
        self.trash = GivenTrash(self.fs,
                                          home_trash=self.home_trash,
                                          volume_trash=self.volume_trash)

    # Purpose: happy path. A well formed .trashinfo in the home trash (on the
    # root volume) is offered for restore with its relative Path= resolved
    # against '/' and its DeletionDate=; choosing it moves the backup copy
    # <trash-dir>/files/<name> back and removes the .trashinfo; no warnings.
    def test_a_trashinfo_is_offered_for_restore(self):
        self.trash.has_a_well_formed_trashinfo("info_path.trashinfo")

        res = self.user.run_restore(['trash-restore', '/'], reply='0',
                                    from_dir='/')

        assert res.output() == '   0 2001-01-01 10:10:10 /name\n'
        assert self.fs.read_file('/name') == 'contents'
        assert not self.fs.exists(self.home_trash + '/info/info_path.trashinfo')
        assert not self.fs.exists(self.home_trash + '/files/info_path')
        assert self.log_messages == []

    # Purpose: a file in the info dir without the .trashinfo extension is
    # not a trashed file: it is not offered and a warning is logged.
    def test_a_non_trashinfo_file_is_skipped_with_a_warning(self):
        self.trash.has_a_non_trashinfo("info_path.non-trashinfo")

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.log_messages == [
            'WARN: Non .trashinfo file in info dir']

    # Purpose: a .trashinfo that cannot be parsed (here: empty, so no Path=)
    # is not offered; the warning reports both the file path and the reason.
    def test_a_non_parsable_trashinfo_is_skipped_with_a_warning(self):
        self.trash.has_a_non_parseable_trashinfo("info_path.trashinfo")

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.log_messages == [
            'WARN: Non parsable trashinfo file: '
            '/home/user/.local/share/Trash/info/info_path.trashinfo, '
            'because Unable to parse Path']

    # Purpose: a .trashinfo that cannot be read (here it is a directory) is
    # not offered and the error is logged as a warning instead of crashing.
    def test_an_unreadable_trashinfo_is_skipped_with_a_warning(self):
        self.trash.has_a_unreadable_trashinfo('info_path.trashinfo')
        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.log_messages == [
            "WARN: IOErrorReadingTrashInfo("
            "path='/home/user/.local/share/Trash/info/info_path.trashinfo', "
            "error='Unable to read: "
            "/home/user/.local/share/Trash/info/info_path.trashinfo')"]

    def test_after_a_non_trashinfo_error_continue(self):
        self.trash.has_a_non_trashinfo('info_path.non-trashinfo')
        self.trash.has_a_well_formed_trashinfo("info_path.trashinfo")

        res = self.user.run_restore(['trash-restore', '/'], reply='0',
                                    from_dir='/')

        assert res.output() == '   0 2001-01-01 10:10:10 /name\n'
        assert self.fs.read_file('/name') == 'contents'
        assert not self.fs.exists(self.home_trash + '/info/info_path.trashinfo')
        assert not self.fs.exists(self.home_trash + '/files/info_path')
        assert self.log_messages == ['WARN: Non .trashinfo file in info dir']
        assert len(self.log_messages) == 1

    def test_after_a_non_parsable_trashinfo_error_continue(self):
        self.trash.has_a_non_parseable_trashinfo('not-parseable.trashinfo')
        self.trash.has_a_well_formed_trashinfo("info_path.trashinfo")

        res = self.user.run_restore(['trash-restore', '/'], reply='0',
                                    from_dir='/')

        assert res.output() == '   0 2001-01-01 10:10:10 /name\n'
        assert self.fs.read_file('/name') == 'contents'
        assert not self.fs.exists(self.home_trash + '/info/info_path.trashinfo')
        assert not self.fs.exists(self.home_trash + '/files/info_path')
        assert self.log_messages == ['WARN: Non parsable trashinfo file: '
                                     '{home_trash}/info/'
                                     'not-parseable.trashinfo, '
                                     'because Unable to parse Path'
                                     .format(home_trash=self.home_trash)]
        assert len(self.log_messages) == 1

    def test_after_unreadable_trashinfo_error_continue(self):
        self.trash.has_a_unreadable_trashinfo('not-readable.trashinfo')
        self.trash.has_a_well_formed_trashinfo("info_path.trashinfo")

        res = self.user.run_restore(['trash-restore', '/'], reply='0',
                                    from_dir='/')

        assert res.output() == '   0 2001-01-01 10:10:10 /name\n'
        assert self.fs.read_file('/name') == 'contents'
        assert not self.fs.exists(self.home_trash + '/info/info_path.trashinfo')
        assert not self.fs.exists(self.home_trash + '/files/info_path')
        assert self.log_messages == [
            "WARN: IOErrorReadingTrashInfo("
            "path='/home/user/.local/share/Trash/info/not-readable.trashinfo', "
            "error='Unable to read: "
            "/home/user/.local/share/Trash/info/not-readable.trashinfo')"]
        assert len(self.log_messages) == 1

    # Purpose: in a volume trash (<volume>/.Trash-$uid) on a volume other
    # than '/', a relative Path= is resolved against that volume.
    def test_a_relative_path_in_a_volume_trash_is_resolved_against_the_volume(
            self):
        self.fs.add_volume('/volume')
        self.trash.has_a_volume_trashinfo('info_path', 'name')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == ('   0 2000-01-01 00:00:00 /volume/name\n'
                                'No files were restored\n')
        assert self.log_messages == []

    # Security (see commit 6cd261cd "Prevent restore from escaping the trash
    # volume"). By the freedesktop trash spec, Path= in a volume trash must be
    # relative to the volume. A .trashinfo that would restore a file outside
    # of the volume must not be offered for restore, otherwise anybody able
    # to write in a trash dir on a removable or shared volume could make the
    # user overwrite arbitrary files.

    # Purpose: the legitimate case still works: a relative Path= inside the
    # volume is offered for restore.
    def test_a_relative_path_inside_the_volume_is_restorable(self):
        self.fs.add_volume('/volume')
        self.trash.has_a_volume_trashinfo('report.txt.trashinfo',
                                          'docs/report.txt',
                                          'report-content')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/',
                                    reply='0')

        assert res.output() == (
            '   0 2000-01-01 00:00:00 /volume/docs/report.txt\n')
        assert self.fs.read_file(
            '/volume/docs/report.txt') == 'report-content'
        assert self.trash.remaining_trashinfo(self.volume_trash) == []
        assert self.trash.remaining_original_copies(self.volume_trash) == []
        assert self.fs.exists(self.home_trash) is False
        assert self.log_messages == []

    # Purpose: an absolute Path= in a volume trash is refused (it could point
    # anywhere, e.g. /etc/passwd).
    def test_an_absolute_path_in_a_volume_trash_is_not_restorable(self):
        self.fs.add_volume('/volume')
        self.trash.has_a_volume_trashinfo('evil', '/etc/passwd')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.log_messages == [
            'WARN: Non parsable trashinfo file: '
            '/volume/.Trash-123/info/evil.trashinfo, '
            'because Path= must be relative for volume trashes']

    # Purpose: a relative Path= that climbs out of the volume with '..' is
    # refused as well.
    def test_a_path_escaping_the_volume_is_not_restorable(self):
        self.fs.add_volume('/volume')
        self.trash.has_a_volume_trashinfo('evil', '../../../etc/shadow')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.log_messages == [
            'WARN: Non parsable trashinfo file: '
            '/volume/.Trash-123/info/evil.trashinfo, '
            'because Path= escapes the volume root']
