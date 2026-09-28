from tests.support.restore.fake_restore_fs import FakePathFs
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.capture_logger import CaptureLogger

HOME_TRASH = '/home/user/.local/share/Trash'
VOLUME_TRASH = '/volume/.Trash-123'


# How trash-restore turns each entry of the info dirs into either a file
# offered for restore or a warning.
# These tests were previously unit tests of TrashedFiles (see commit
# c4a2c055 for their documented purpose), now rewritten against the command.
class TestRestoreReadingTrashinfoFiles:
    def setup_method(self):
        self.fs = FakePathFs()
        self.logger = CaptureLogger()
        self.user = RestoreUser(environ={'HOME': '/home/user'},
                                uid=123,
                                file_reader=self.fs,
                                path_read_fs=self.fs,
                                write_fs=self.fs,
                                listing_fs=self.fs,
                                version='1.0',
                                volumes=self.fs,
                                volume_path_fs=self.fs,
                                logger=self.logger)

    # Purpose: happy path. A well formed .trashinfo in the home trash (on the
    # root volume) is offered for restore with its relative Path= resolved
    # against '/' and its DeletionDate=; choosing it moves the backup copy
    # <trash-dir>/files/<name> back and removes the .trashinfo; no warnings.
    def test_a_trashinfo_is_offered_for_restore(self):
        self.fs.add_file(HOME_TRASH + '/info/info_path.trashinfo',
                         b'[Trash Info]\n'
                         b'Path=name\n'
                         b'DeletionDate=2001-01-01T10:10:10\n')
        self.fs.add_file(HOME_TRASH + '/files/info_path', b'contents')

        res = self.user.run_restore(['trash-restore', '/'], reply='0',
                                    from_dir='/')

        assert res.output() == '   0 2001-01-01 10:10:10 /name\n'
        assert self.fs.contents_of('/name') == 'contents'
        assert not self.fs.exists(HOME_TRASH + '/info/info_path.trashinfo')
        assert not self.fs.exists(HOME_TRASH + '/files/info_path')
        assert self.logger.captured == []

    # Purpose: a file in the info dir without the .trashinfo extension is
    # not a trashed file: it is not offered and a warning is logged.
    def test_a_non_trashinfo_file_is_skipped_with_a_warning(self):
        self.fs.add_file(HOME_TRASH + '/info/info_path.non-trashinfo')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.logger.captured == [
            'WARN: Non .trashinfo file in info dir']

    # Purpose: a .trashinfo that cannot be parsed (here: empty, so no Path=)
    # is not offered; the warning reports both the file path and the reason.
    def test_a_non_parsable_trashinfo_is_skipped_with_a_warning(self):
        self.fs.add_file(HOME_TRASH + '/info/info_path.trashinfo', b'')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.logger.captured == [
            'WARN: Non parsable trashinfo file: '
            '/home/user/.local/share/Trash/info/info_path.trashinfo, '
            'because Unable to parse Path']

    # Purpose: a .trashinfo that cannot be read (here it is a directory) is
    # not offered and the error is logged as a warning instead of crashing.
    def test_an_unreadable_trashinfo_is_skipped_with_a_warning(self):
        self.fs.fake_fs.makedirs(HOME_TRASH + '/info/info_path.trashinfo',
                                 0o755)

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.logger.captured == [
            "WARN: IOErrorReadingTrashInfo("
            "path='/home/user/.local/share/Trash/info/info_path.trashinfo', "
            "error='Unable to read: "
            "/home/user/.local/share/Trash/info/info_path.trashinfo')"]

    def test_after_a_non_trashinfo_error_continue(self):
        # not a trashinfo
        self.fs.add_file(HOME_TRASH + '/info/info_path.non-trashinfo')

        # trashinfo + original copy
        self.fs.add_file(HOME_TRASH + '/info/info_path.trashinfo',
                         b'[Trash Info]\n'
                         b'Path=name\n'
                         b'DeletionDate=2001-01-01T10:10:10\n')
        self.fs.add_file(HOME_TRASH + '/files/info_path', b'contents')

        res = self.user.run_restore(['trash-restore', '/'], reply='0',
                                    from_dir='/')

        assert res.output() == '   0 2001-01-01 10:10:10 /name\n'
        assert self.fs.contents_of('/name') == 'contents'
        assert not self.fs.exists(HOME_TRASH + '/info/info_path.trashinfo')
        assert not self.fs.exists(HOME_TRASH + '/files/info_path')
        assert self.logger.captured == ['WARN: Non .trashinfo file in info dir']
        assert len(self.logger.captured) == 1

    def test_after_a_non_parsable_trashinfo_error_continue(self):
        # add non parsable
        self.fs.add_file(HOME_TRASH + '/info/not-parseable.trashinfo', b'')

        # trashinfo + original copy
        self.fs.add_file(HOME_TRASH + '/info/info_path.trashinfo',
                         b'[Trash Info]\n'
                         b'Path=name\n'
                         b'DeletionDate=2001-01-01T10:10:10\n')
        self.fs.add_file(HOME_TRASH + '/files/info_path', b'contents')

        res = self.user.run_restore(['trash-restore', '/'], reply='0',
                                    from_dir='/')

        assert res.output() == '   0 2001-01-01 10:10:10 /name\n'
        assert self.fs.contents_of('/name') == 'contents'
        assert not self.fs.exists(HOME_TRASH + '/info/info_path.trashinfo')
        assert not self.fs.exists(HOME_TRASH + '/files/info_path')
        assert self.logger.captured == ['WARN: Non parsable trashinfo file: '
                                        '/home/user/.local/share/Trash/info/'
                                        'not-parseable.trashinfo, '
                                        'because Unable to parse Path']
        assert len(self.logger.captured) == 1

    def test_after_unreadable_trashinfo_error_continue(self):
        self.fs.fake_fs.makedirs(HOME_TRASH + '/info/not_parseable.trashinfo',
                                 0o755)

        # trashinfo + original copy
        self.fs.add_file(HOME_TRASH + '/info/info_path.trashinfo',
                         b'[Trash Info]\n'
                         b'Path=name\n'
                         b'DeletionDate=2001-01-01T10:10:10\n')
        self.fs.add_file(HOME_TRASH + '/files/info_path', b'contents')

        res = self.user.run_restore(['trash-restore', '/'], reply='0',
                                    from_dir='/')


        assert res.output() == '   0 2001-01-01 10:10:10 /name\n'
        assert self.fs.contents_of('/name') == 'contents'
        assert not self.fs.exists(HOME_TRASH + '/info/info_path.trashinfo')
        assert not self.fs.exists(HOME_TRASH + '/files/info_path')
        assert self.logger.captured == [
            "WARN: IOErrorReadingTrashInfo("
            "path='/home/user/.local/share/Trash/info/not_parseable.trashinfo', "
            "error='Unable to read: "
            "/home/user/.local/share/Trash/info/not_parseable.trashinfo')"]
        assert len(self.logger.captured) == 1

    # Purpose: in a volume trash (<volume>/.Trash-$uid) on a volume other
    # than '/', a relative Path= is resolved against that volume.
    def test_a_relative_path_in_a_volume_trash_is_resolved_against_the_volume(self):
        self.fs.add_volume('/volume')
        self.add_volume_trashinfo('info_path', 'name')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == ('   0 2000-01-01 00:00:00 /volume/name\n'
                                'No files were restored\n')
        assert self.logger.captured == []

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
        self.add_volume_trashinfo('good', 'docs/report.txt')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == (
            '   0 2000-01-01 00:00:00 /volume/docs/report.txt\n'
            'No files were restored\n')

    # Purpose: an absolute Path= in a volume trash is refused (it could point
    # anywhere, e.g. /etc/passwd).
    def test_an_absolute_path_in_a_volume_trash_is_not_restorable(self):
        self.fs.add_volume('/volume')
        self.add_volume_trashinfo('evil', '/etc/passwd')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.logger.captured == [
            'WARN: Non parsable trashinfo file: '
            '/volume/.Trash-123/info/evil.trashinfo, '
            'because Path= must be relative for volume trashes']

    # Purpose: a relative Path= that climbs out of the volume with '..' is
    # refused as well.
    def test_a_path_escaping_the_volume_is_not_restorable(self):
        self.fs.add_volume('/volume')
        self.add_volume_trashinfo('evil', '../../../etc/shadow')

        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        assert res.output() == "No files trashed from current dir ('/')\n"
        assert self.logger.captured == [
            'WARN: Non parsable trashinfo file: '
            '/volume/.Trash-123/info/evil.trashinfo, '
            'because Path= escapes the volume root']

    def add_volume_trashinfo(self, name, path_line):
        self.fs.add_file(VOLUME_TRASH + '/info/%s.trashinfo' % name,
                         ('[Trash Info]\n'
                          'Path=%s\n'
                          'DeletionDate=2000-01-01T00:00:00\n' % path_line
                          ).encode('utf-8'))
        self.fs.add_file(VOLUME_TRASH + '/files/%s' % name)
