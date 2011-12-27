from nose.tools import istest
from trashcli.trash import RestoreCmd
from StringIO import StringIO

from .files import require_empty_dir
from .output_collector import OutputCollector
from trashinfo import (a_trashinfo, a_trashinfo_without_date,
                       a_trashinfo_with_invalid_date)

@istest
class describe_restore_trash:
    @istest
    def it_should_do_nothing_when_no_file_have_been_removed(self):
        require_empty_dir('XDG_DATA_HOME')

        exit = [].append
        input = lambda x: ""
        out = OutputCollector()

        RestoreCmd(
            stdout  = out,
            stderr  = StringIO(),
            environ = {'XDG_DATA_HOME':'XDG_DATA_HOME'},
            exit    = exit,
            input   = input).run()

        out.should_match('No files trashed from current dir.+')

    @istest
    def it_should_do_nothing_when_no_file_have_been_removed(self):
        require_empty_dir('XDG_DATA_HOME')
        info_dir  = 'XDG_DATA_HOME/Trash/info'
        files_dir = 'XDG_DATA_HOME/Trash/files'
        from .files import write_file
        write_file('%s/foo.trashinfo' % info_dir, a_trashinfo('/foo'))
        write_file('%s/foo.trashinfo' % files_dir)

        exit = [].append
        input = lambda x: ""
        out = OutputCollector()

        RestoreCmd(
            stdout  = out,
            stderr  = StringIO(),
            environ = {'XDG_DATA_HOME':'XDG_DATA_HOME'},
            exit    = exit,
            input   = input).run()

        out.should_match('No files trashed from current dir.+')

