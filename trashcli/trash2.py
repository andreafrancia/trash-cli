# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

import os

def do_nothing(*argv, **argvk): pass
class _FileReader:
    def __init__(self):
        self.contents_of = contents_of
        self.exists = os.path.exists
        self.is_sticky_dir = is_sticky_dir
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry

def is_sticky_dir(path):
    import os
    return os.path.isdir(path) and has_sticky_bit(path)

def contents_of(path):
    return file(path).read()

class _FileRemover:
    def remove_file(self, path):
        return os.remove(path)
    def remove_file_if_exists(self,path):
        if os.path.exists(path): self.remove_file(path)

from .list_mount_points import mount_points
from . import version
from datetime import datetime

class ListCmd():
    def __init__(self, out, err, environ, 
                 getuid        = os.getuid,
                 list_volumes  = mount_points,
                 is_sticky_dir = is_sticky_dir,
                 file_reader   = _FileReader(),
                 version       = version):

        self.out         = out
        self.err         = err
        self.file_reader = file_reader
        self.infodirs    = AvailableTrashDir(environ, getuid, list_volumes,
                                             is_sticky_dir)
        self.version     = version

    def run(self, *argv):
        parse=Parser()
        parse.on_help(PrintHelp(self.description, self.println))
        parse.on_version(PrintVersion(self.println, self.version))
        parse.as_default(self.list_trash)
        parse(argv)
    def list_trash(self):
        self.infodirs.for_each_infodir(self.file_reader,
                                       self.list_contents)
    def description(self, program_name, printer):
        printer.usage('Usage: %s [OPTIONS...]' % program_name)
        printer.summary('List trashed files')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()
    def list_contents(self, info_dir):
        info_dir.each_parsed_trashinfo(
                on_parse       = self.print_entry,
                on_read_error  = self.print_read_error,
                on_parse_error = self.print_parse_error)
    def print_parse_error(self, offending_file, reason):
        self.error("Parse Error: %s: %s" % (offending_file, reason))
    def print_read_error(self, error):
        self.error(str(error))
    def print_entry(self, maybe_deletion_date, original_location):
        self.println("%s %s" %(maybe_deletion_date,
                               original_location))
    def println(self, line):
        self.out.write(line+'\n')
    def error(self, line):
        self.err.write(line+'\n')

class Parser:
    def __init__(self):
        self.default_action = do_nothing
        self.argument_action = do_nothing
        self.short_options = ''
        self.long_options = []
        self.actions = dict()
    def __call__(self, argv):
        program_name = argv[0]
        from getopt import getopt
        options, arguments = getopt(argv[1:], 
                                    self.short_options, 
                                    self.long_options)
    
        for option, value in options:
            if option in self.actions:
                self.actions[option](program_name)
                return
        for argument in arguments:
            self.argument_action(argument)
        self.default_action()
    def on_help(self, action):
        self.add_option('help', action, 'h')

    def on_version(self, action):
        self.add_option('version', action)

    def add_option(self, long_option, action, short_aliases=''):
        self.long_options.append(long_option)
        self.actions['--' + long_option] = action
        for short_alias in short_aliases:
            self.add_short_option(short_alias, action)

    def add_short_option(self, short_option, action):
        self.short_options += short_option
        self.actions['-' + short_option] = action

    def on_argument(self, argument_action):
        self.argument_action = argument_action
    def as_default(self, default_action):
        self.default_action = default_action

class EmptyCmd():
    def __init__(self, out, err, environ, 
                 now           = datetime.now,
                 file_reader   = _FileReader(),
                 list_volumes  = mount_points,
                 getuid        = os.getuid,
                 is_sticky_dir = is_sticky_dir,
                 file_remover  = _FileRemover(),
                 version       = version):

        self.out          = out
        self.err          = err
        self.file_reader  = file_reader 
        self.infodirs     = AvailableTrashDir(environ, getuid, list_volumes,
                                              is_sticky_dir)

        self.now          = now
        self.file_remover = file_remover
        self.version      = version

    def run(self, *argv):
        self.date_criteria = always
        parse = Parser()
        parse.on_help(PrintHelp(self.description, self.println))
        parse.on_version(PrintVersion(self.println, self.version))
        parse.on_argument(self.set_deletion_date_criteria)
        parse.as_default(self._delete_according_criteria)
        parse(argv)

    def set_deletion_date_criteria(self, arg):
        self.date_criteria = OlderThan(int(arg), self.now)

    def description(self, program_name, printer):
        printer.usage('Usage: %s [days]' % program_name)
        printer.summary('Purge trashed files.')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()
    def is_int(self, text):
        try:
            int(text)
            return True
        except ValueError:
            return False
    def _delete_according_criteria(self):
        self.infodirs.for_each_infodir(self.file_reader,
                                       self._empty_trashdir_according_criteria)
    def _empty_trashdir_according_criteria(self, info_dir):
        janitor=Janitor(self.date_criteria, self.file_remover)
        janitor.swep(info_dir)
    def println(self, line):
        self.out.write(line + '\n')

class PrintHelp:
    def __init__(self, description, println):
        class Printer:
            def __init__(self, println):
                self.println = println
            def usage(self, usage):
                self.println(usage)
                self.println('')
            def summary(self, summary):
                self.println(summary)
                self.println('')
            def options(self, *line_describing_option):
                self.println('Options:')
                for line in line_describing_option:
                    self.println(line)
                self.println('')
            def bug_reporting(self):
                self.println("Report bugs to http://code.google.com/p/trash-cli/issues")
        self.description  = description
        self.printer      = Printer(println)

    def __call__(self, program_name):
        self.description(program_name, self.printer)

class PrintVersion:
    def __init__(self, println, version):
        self.println      = println
        self.version      = version
    def __call__(self, program_name):
        self.println("%s %s" % (program_name, self.version))

class Janitor:
    def __init__(self, date_criteria, file_remover):
        self.date_criteria = date_criteria
        self.file_remover = file_remover
    def swep(self, infodir):
        infodir.for_all_files_satisfying(self.date_criteria,
                self.remove_trash)
        infodir.for_all_orphans(self.remove_file)
    def remove_file(self, path):
        self.file_remover.remove_file(path)
    def remove_trash(self, trash):
        self.file_remover.remove_file_if_exists(trash.path_to_backup_copy())
        self.file_remover.remove_file(trash.path_to_trashinfo())

def curry_add_info(on_info_dir):
    def on_trash_dir(trash_dir, volume):
        import os
        info_dir = os.path.join(trash_dir, 'info')
        on_info_dir(info_dir, volume)
    return on_trash_dir

class AvailableTrashDir:
    def __init__(self, environ, getuid, list_volumes, 
                 is_sticky_dir= lambda path: True):
        self.environ       = environ
        self.getuid        = getuid
        self.list_volumes  = list_volumes
        self.is_sticky_dir = is_sticky_dir
    def for_each_infodir(self, file_reader, action):
        def action2(info_dir_path, volume_path):
            infodir = InfoDir(file_reader, info_dir_path, volume_path)
            action(infodir)
        self.for_home_trashcan(curry_add_info(action2))
        self.for_each_volume_trashcans(curry_add_info(action2))
    def for_each_infodir_and_volume(self, action):
        self.for_home_trashcan(action)
        self.for_each_volume_trashcans(action)
    def for_home_trashcan(self, action):
        if 'XDG_DATA_HOME' in self.environ:
            action('%(XDG_DATA_HOME)s/Trash' % self.environ, '/')
        elif 'HOME' in self.environ:
            action('%(HOME)s/.local/share/Trash' % self.environ, '/')
    def for_each_volume_trashcans(self, action):
        from os.path import join
        for volume in self.list_volumes():
            top_trash_dir = join(volume, '.Trash')
            if self.is_sticky_dir(top_trash_dir):
                action(join(top_trash_dir, str(self.getuid())), volume)
            
            action(join(volume, '.Trash-%s' % self.getuid()), volume)

def always(deletion_date): return True
class OlderThan:
    def __init__(self, days_ago, now):
        from datetime import timedelta
        self.limit_date = now() - timedelta(days=days_ago)
    def __call__(self, deletion_date):
        return deletion_date < self.limit_date

class FilterByDateCriteria:
    def __init__(self, date_criteria, action):
        self.date_criteria = date_criteria
        self.action        = action
    def __call__(self, trashinfo, parsed):
        if self.date_criteria(parsed.deletion_date()):
            self.action(trashinfo)
class InfoDir:
    def __init__(self, file_reader, path, volume_path):
        self.path        = path
        self.file_reader = file_reader
        self.volume_path = volume_path
    def for_all_orphans(self, action):
        for entry in self._files():
            trashinfo_path = self._trashinfo_path_from_file(entry)
            file_path = os.path.join(self._files_dir(), entry)
            if not self.file_reader.exists(trashinfo_path): action(file_path)
    def _files(self):
        return self._entries_if_dir_exists(self._files_dir())
    def _entries_if_dir_exists(self, path):
        return self.file_reader.entries_if_dir_exists(path)
    def for_all_files_satisfying(self, date_criteria, action):
        self.each_trashinfo_lazily_parsed(
                FilterByDateCriteria(date_criteria, action))

    def each_trashinfo_lazily_parsed(self, action):
        for trashinfo in self._trashinfos():

            file_being_parsed = trashinfo.path_to_trashinfo()
            def contents(): return self.file_reader.contents_of(file_being_parsed)
            parser = LazyTrashInfoParser(contents, self.volume_path) 

            action(trashinfo, parser)

    def each_parsed_trashinfo(self, on_parse, on_read_error, on_parse_error):
        class WakingUpParser:
            def __call__(self, trashinfo, parser):
                try:
                    maybe_deletion_date = maybe_date(parser.deletion_date)
                    original_location   = parser.original_location()
                except ParseError, e:
                    on_parse_error(trashinfo.path_to_trashinfo(), e.message)
                except IOError, e:
                    on_read_error(e)
                else:
                    on_parse(maybe_deletion_date, original_location)
        
        self.each_trashinfo_lazily_parsed(WakingUpParser())
            
    def _trashinfos(self):
        for entry in self._trashinfo_entries():
            yield self._trashinfo(entry)
    def _trashinfo(self, entry):
        class TrashInfo:
            def __init__(self, info_dir, files_dir, entry, file_reader,
                         volume_path):
                self.info_dir    = info_dir      
                self.files_dir   = files_dir     
                self.entry       = entry         
            def path_to_backup_copy(self):
                entry = self.entry[:-len('.trashinfo')]
                return os.path.join(self.files_dir, entry)
            def path_to_trashinfo(self):
                return os.path.join(self.info_dir, self.entry)
        return TrashInfo(self.path, 
                         self._files_dir(), 
                         entry, 
                         self.file_reader, 
                         self.volume_path)
    def _trashinfo_path_from_file(self, file_entry):
        return os.path.join(self.path, file_entry + '.trashinfo')
    def _files_dir(self):
        return os.path.join(os.path.dirname(self.path), 'files')
    def _trashinfo_entries(self):
        for entry in self._entries_if_dir_exists(self.path):
            if entry.endswith('.trashinfo'):
                yield entry
    def _trashinfo_path(self, entry):
        return os.path.join(self.path, entry)

class ParseError(ValueError): pass

class LazyTrashInfoParser:
    def __init__(self, contents, volume_path):
        self.contents    = contents
        self.volume_path = volume_path
    def deletion_date(self):
        return parse_deletion_date(self.contents())
    def _path(self):
        return parse_path(self.contents())
    def original_location(self):
        return os.path.join(self.volume_path, self._path())

def maybe_parse_deletion_date(contents):
    return maybe_date(lambda:parse_deletion_date(contents))

def maybe_date(parsing_closure):
    try:
        date = parsing_closure()
    except ValueError:
        return unknown_date()
    else:
        if date: return date
    return unknown_date()

def unknown_date():
    return '????-??-?? ??:??:??'

def parse_deletion_date(contents):
    from datetime import datetime 
    for line in contents.split('\n'):
        if line.startswith('DeletionDate='):
            return datetime.strptime(line, "DeletionDate=%Y-%m-%dT%H:%M:%S")
def parse_path(contents):
    import urllib
    for line in contents.split('\n'):
        if line.startswith('Path='):
            return urllib.unquote(line[len('Path='):])
    raise ParseError('Unable to parse Path')

def has_sticky_bit(path):
    import os
    import stat
    return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX

