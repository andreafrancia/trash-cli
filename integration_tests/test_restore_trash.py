import os
from nose.tools import istest
from trashcli.trash import RestoreCmd

from .files import require_empty_dir
from .output_collector import OutputCollector
from trashinfo import a_trashinfo

@istest
class describe_restore_trash:
    @istest
    def it_should_do_nothing_when_no_file_have_been_found_in_current_dir(self):

        self.when_running_restore_trash()
        self.output_should_match('No files trashed from current dir.+')

    @istest
    def it_should_show_the_file_deleted_from_the_current_dir(self):

        self.having_a_trashed_file('/foo/bar')
        self.when_running_restore_trash(from_dir='/foo')
        self.output_should_match(
            '   0 2000-01-01 00:00:01 /foo/bar\n.*\n')
        self.error_should_be('')

    @istest
    def it_should_restore_the_file_selected_by_the_user(self):

        self.having_a_file_trashed_from_current_dir('foo')
        self.when_running_restore_trash(
                from_dir=os.getcwd(), 
                with_user_typing = '0')

        self.file_should_have_been_restored('foo')
    
    @istest
    def it_should_exit_gracefully_when_user_selects_nothing(self):

        self.having_a_trashed_file('/foo/bar')
        self.when_running_restore_trash( from_dir='/foo', 
                                         with_user_typing = '')
        self.output_should_match(
            '.*\nExiting\n')
        self.error_should_be('')

    @istest
    def it_should_refuse_overwriting_existing_file(self):

        self.having_a_file_trashed_from_current_dir('foo')
        file('foo', 'a+').close()
        os.chmod('foo', 000)
        self.when_running_restore_trash(from_dir=current_dir(),
                                        with_user_typing = '0')
        self.error_should_be('Refusing to overwrite existing file "foo".\n')

    def setUp(self):
        require_empty_dir('XDG_DATA_HOME')

        trashcan = TrashCan('XDG_DATA_HOME/Trash')
        self.having_a_trashed_file = trashcan.make_trashed_file

        out = OutputCollector()
        err = OutputCollector()
        self.when_running_restore_trash = RestoreTrashRunner(out, err,
                                                             'XDG_DATA_HOME')
        self.output_should_match = out.should_match
        self.error_should_be = err.should_be

    def having_a_file_trashed_from_current_dir(self, filename):
        self.having_a_trashed_file(os.path.join(os.getcwd(), filename))
        if os.path.exists(filename):
            os.remove(filename)
        assert not os.path.exists(filename)

    def file_should_have_been_restored(self, filename):
        assert os.path.exists(filename)

def current_dir():
    return os.getcwd()

class RestoreTrashRunner:
    def __init__(self, out, err, XDG_DATA_HOME):
        self.environ = {'XDG_DATA_HOME': XDG_DATA_HOME}
        self.out = out
        self.err = err
    def __call__(self, from_dir='/', with_user_typing=''):
        RestoreCmd(
            stdout  = self.out,
            stderr  = self.err,
            environ = self.environ,
            exit    = [].append,
            input   = lambda msg: with_user_typing,
            curdir  = lambda: from_dir
        ).run()

class TrashCan:
    def __init__(self, path):
        self.path = path
    def make_trashed_file(self, path):
        from .files import write_file
        write_file('%s/info/foo.trashinfo' % self.path, a_trashinfo(path))
        write_file('%s/files/foo' % self.path)

