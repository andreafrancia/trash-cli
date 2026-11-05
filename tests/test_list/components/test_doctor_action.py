import os

from six import StringIO

from trashcli.list.list_trash_action import DoctorAction, DoctorArgs
from trashcli.trash_dirs_scanner import TrashDir, trash_dir_found


class StubSelector:
    def __init__(self, paths):
        self.paths = paths

    def select(self, all_users_flag, user_specified_dirs, environ, uid):
        for path in self.paths:
            yield trash_dir_found, TrashDir(path, '/')


class StubDirReader:
    def __init__(self, entries=None, errors=None):
        self.entries = entries or {}
        self.errors = errors or {}

    def entries_if_dir_exists(self, path):
        # A generator, like the real reader, so an error surfaces during
        # iteration and not when the reader is called.
        if path in self.errors:
            raise self.errors[path]
        for entry in self.entries.get(path, []):
            yield entry


def make_action(paths, dir_reader):
    out = StringIO()
    err = StringIO()
    action = DoctorAction({}, 123, StubSelector(paths), out, err, dir_reader,
                          None)
    return action, out, err


def test_doctor_reports_an_enumeration_error_instead_of_crashing():
    info_dir = os.path.join('first-trash', 'info')
    reader = StubDirReader(errors={info_dir: OSError('cannot list')})
    action, out, err = make_action(['first-trash'], reader)

    action.run_action(DoctorArgs(trash_dirs=[], all_users=False))

    assert err.getvalue() == 'cannot list\n'
    assert out.getvalue() == ''


def test_doctor_keeps_scanning_the_next_trash_dir():
    first_info = os.path.join('first-trash', 'info')
    second_info = os.path.join('second-trash', 'info')
    reader = StubDirReader(entries={second_info: ['not-a-trashinfo']},
                           errors={first_info: OSError('cannot list')})
    action, out, err = make_action(['first-trash', 'second-trash'], reader)

    action.run_action(DoctorArgs(trash_dirs=[], all_users=False))

    assert err.getvalue() == 'cannot list\n'
    assert out.getvalue() == (
        'Non .trashinfo file in info dir: %s\n'
        % os.path.join(second_info, 'not-a-trashinfo'))
