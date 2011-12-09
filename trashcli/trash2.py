import os

class _FileReader:
    def contents_of(self, path):
        return file(path).read()
    def exists(self, path):
        return os.path.exists(path)
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry

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
                 getuid       = os.getuid,
                 list_volumes = mount_points,
                 file_reader  = _FileReader()):
        self.out         = out
        self.infodirs    = InfoDirsFinder(environ, getuid, list_volumes)
        self.file_reader = file_reader
    def run(self, *argv):
        self.infodirs.for_each_infodir(self.file_reader,
                                       self.list_contents)
    def list_contents(self, info_dir):
        info_dir.for_all_trashinfos(self.print_entry,
                                    on_parse_error=self.print_parse_error)
    def print_parse_error(self, offending_file):
        self.err.write("Problems parsing `XDG_DATA_HOME/Trash/info/empty.trashinfo'")
    def print_entry(self, deletion_date, original_location):
        self.println("%s %s" %(deletion_date, original_location))
    def println(self, line):
        self.out.write(line+'\n')

class EmptyCmd():
    def __init__(self, out, err, environ, 
                 now          = datetime.now,
                 file_reader  = _FileReader(),
                 list_volumes = mount_points,
                 getuid       = os.getuid,
                 file_remover = _FileRemover(),
                 version      = version):
        self.out          = out
        self.err          = err
        self.now          = now
        self.file_reader  = file_reader 
        self.file_remover = file_remover
        self.infodirs     = InfoDirsFinder(environ, getuid, list_volumes)
        self.version      = version
    def run(self, *argv):
        self.date_criteria = always
        action             = self._delete_according_criteria
        self.program_name  = argv[0]
        for arg in argv[1:]:
            if arg == '--help' or arg == '-h':
                action = self.print_help
                break
            if arg == '--version' :
                action = self.print_version
                break
            elif self.is_int(arg):
                self.date_criteria = OlderThan(int(arg), self.now)
        action()
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
    def print_version(self):
        self.out.write("%s %s\n" % (self.program_name, self.version))
    def print_help(self):
        self.out.write("""\
Usage: %(program_name)s [days]

Purge trashed files.

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""" % {
        'program_name':self.program_name
        })

class Janitor:
    def __init__(self, date_criteria, file_remover):
        self.date_criteria = date_criteria
        self.file_remover = file_remover
    def swep(self, infodir):
        infodir.for_all_files_satisfying(self.date_criteria, self.remove_both)
        infodir.for_all_orphan(self.remove_file)
    def remove_file(self, path):
        self.file_remover.remove_file(path)
    def remove_both(self, trashinfo_path, file_path):
        self.file_remover.remove_file_if_exists(file_path)
        self.file_remover.remove_file(trashinfo_path)

class InfoDirsFinder:
    def __init__(self, environ, getuid, list_volumes):
        self.environ      = environ
        self.getuid       = getuid
        self.list_volumes = list_volumes
    def for_each_infodir(self, file_reader, action):
        for info_dir_path, volume_path in self._paths():
            infodir = InfoDir(file_reader, info_dir_path, volume_path)
            action(infodir)
    def _paths(self):
        from os.path import join 
        if 'XDG_DATA_HOME' in self.environ:
            yield ('%(XDG_DATA_HOME)s/Trash/info' % self.environ, None)
        elif 'HOME' in self.environ:
            yield ('%(HOME)s/.local/share/Trash/info' % self.environ, None)
        for volume in self.list_volumes():
            yield (join(volume, '.Trash', str(self.getuid()), 'info'), volume)
            yield (join(volume, '.Trash-%s' % self.getuid() , 'info'), volume)
def always(deletion_date): return True
class OlderThan:
    def __init__(self, days_ago, now):
        from datetime import timedelta
        self.limit_date = now() - timedelta(days=days_ago)
    def __call__(self, deletion_date):
        return deletion_date < self.limit_date

class InfoDir:
    def __init__(self, file_reader, path, volume_path):
        self.path        = path
        self.file_reader = file_reader
        self.volume_path = volume_path
    def for_all_orphan(self, action):
        for entry in self._files():
            trashinfo_path = self._trashinfo_path_from_file(entry)
            file_path = os.path.join(self._files_dir(), entry)
            if not self.file_reader.exists(trashinfo_path): action(file_path)
    def _files(self):
        return self._entries_if_dir_exists(self._files_dir())
    def _entries_if_dir_exists(self, path):
        return self.file_reader.entries_if_dir_exists(path)
    def for_all_files_satisfying(self, date_criteria, action):
        def action2(path, deletion_date):
            if(date_criteria(deletion_date)):
                path_to_backup_copy = trashinfo.path_to_backup_copy()
                path_to_trashinfo   = trashinfo.path_to_trashinfo()
                action(path_to_trashinfo, path_to_backup_copy)
        class Boh:
            def __init__(self, contents_of):
                self.contents_of = contents_of

        for trashinfo in self._trashinfos():
            contents          = self.file_reader.contents_of(trashinfo.path_to_trashinfo())
            deletion_date     = read_deletion_date(contents)
            path              = read_path(contents)
            action2(path, deletion_date)

    def for_all_trashinfos(self, action, on_parse_error):
        def action2(trashinfo):
            deletion_date = trashinfo.deletion_date()
            path = trashinfo.read_path()
            original_location = os.path.join(self.volume_path, path)

            action(
                deletion_date     = deletion_date,
                original_location = original_location)
        self.for_all_deletion_date_and_path(action2, on_parse_error)

    def for_all_deletion_date_and_path(self, action2, on_parse_error):
        for trashinfo in self._trashinfos():
            action2(trashinfo)

    def _trashinfo(self, entry):
        class TrashInfo:
            def __init__(self, info_dir, files_dir, entry, file_reader):
                self.info_dir    = info_dir      
                self.files_dir   = files_dir     
                self.entry       = entry         
                self.file_reader = file_reader
            def path_to_backup_copy(self):
                # used by trash-empty
                entry = self.entry[:-len('.trashinfo')]
                return os.path.join(self.files_dir, entry)
            def path_to_trashinfo(self):
                # used by trash-empty
                return os.path.join(self.info_dir, self.entry)
            def contents(self):
                return self.file_reader.contents_of(self.path_to_trashinfo())
            def deletion_date(self):
                return read_deletion_date(self.contents())
            def read_path(self):
                return read_path(self.contents())
        return TrashInfo(self.path, 
                         self._files_dir(), 
                         entry, 
                         self.file_reader)
    def _trashinfo_path_from_file(self, file_entry):
        return os.path.join(self.path, file_entry + '.trashinfo')
    def _files_dir(self):
        return os.path.join(os.path.dirname(self.path), 'files')
    def _trashinfos(self):
        for entry in self._trashinfo_entries():
            yield self._trashinfo(entry)
    def _trashinfo_entries(self):
        for entry in self._entries_if_dir_exists(self.path):
            if entry.endswith('.trashinfo'):
                yield entry
    def _trashinfo_path(self, entry):
        return os.path.join(self.path, entry)

def do_nothing(*argv, **argvk): pass


class TrashInfoParser:
    def __init__(self, contents, on_error = do_nothing):
        self.errors   = on_error
        self.contents = contents
    def deletion_date(self):
        return read_deletion_date(self.contents)
    def original_location(self, volume):
        return os.path.join(volume, read_path(self.contents))

def read_deletion_date(contents):
    from datetime import datetime 
    for line in contents.split('\n'):
        if line.startswith('DeletionDate='):
            return datetime.strptime(line, "DeletionDate=%Y-%m-%dT%H:%M:%S")

def read_path(contents):
    import urllib
    for line in contents.split('\n'):
        if line.startswith('Path='):
            return urllib.unquote(line[len('Path='):])

