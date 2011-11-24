import os

class FileSystem:
    def contents_of(self, path):
        return file(path).read()
    def exists(self, path):
        return os.path.exists(path)
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry
    def if_exists(self, path, action):
        if self.exists(path): action()
    def if_does_not_exists(self, path, action):
        if not self.exists(path): action()

class FileRemover:
    def remove_file(self, path):
        return os.remove(path)
    def remove_file_if_exists(self,path):
        if os.path.exists(path): self.remove_file(path)

from .list_mount_points import mount_points

from . import version
class EmptyCmd():
    from datetime import datetime
    def __init__(self, out, err, environ, now = datetime.now, 
                 file_reader = FileSystem(), list_volumes=mount_points, 
                 getuid=os.getuid, file_remover = FileRemover(),
                 version = version):
        self.out          = out
        self.err          = err
        self.now          = now
        self.file_reader  = file_reader 
        self.file_remover = file_remover
        self.infodirs     = InfoDirs(environ, getuid, list_volumes)
        self.version      = version
    def run(self, *argv):
        self.date_criteria = always
        action             = self.delete_according_criteria
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
                action = self.delete_according_criteria
        action()
    def is_int(self, text):
        try:
            int(text)
            return True
        except ValueError:
            return False
    def delete_according_criteria(self):
        janitor = Janitor(self.date_criteria, self.file_remover)
        def invoke(info_dir_path):
            infodir = InfoDir(self.file_reader, info_dir_path)
            janitor(infodir)
        self.infodirs.for_each_path(invoke)
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
    def __call__(self, infodir):
        infodir.for_all_files_satisfying(self.date_criteria, self.remove_both)
        infodir.for_all_orphan(self.remove_file)
    def remove_file(self, path):
        self.file_remover.remove_file(path)
    def remove_both(self, trashinfo_path, file_path):
        self.file_remover.remove_file_if_exists(file_path)
        self.file_remover.remove_file(trashinfo_path)
class InfoDirs:
    def __init__(self, environ, getuid, list_volumes):
        self.environ      = environ
        self.getuid       = getuid
        self.list_volumes = list_volumes
    def paths(self):
        if 'XDG_DATA_HOME' in self.environ:
            yield '%s/Trash/info' % self.environ['XDG_DATA_HOME']
        elif 'HOME' in self.environ:
            yield '%s/.local/share/Trash/info' % self.environ['HOME']
        for volume in self.list_volumes():
            yield '%(volume)s/.Trash/%(uid)s/info' % { 'volume': volume, 'uid': self.getuid()}
            yield '%(volume)s/.Trash-%(uid)s/info' % { 'volume': volume, 'uid': self.getuid()}
    def for_each_path(self, callable):
        for path in self.paths():
            callable(path)
def always(deletion_date): return True
class OlderThan:
    def __init__(self, days_ago, now):
        from datetime import timedelta
        self.limit_date = now() - timedelta(days=days_ago)
    def __call__(self, deletion_date):
        return deletion_date < self.limit_date
class InfoDir:
    def __init__(self, file_reader, path):
        self.path = path
        self.file_reader = file_reader
    def for_all_orphan(self, callable):
        for entry in self._files():
            trashinfo_path = self._trashinfo_path(entry)
            file_path = os.path.join(self._files_dir(), entry)
            if not self.file_reader.exists(trashinfo_path): callable(file_path)
    def _deletion_date(self, entry):
        return read_deletion_date(self.file_reader.contents_of(self._trashinfo_path(entry)))
    def _files(self):
        return self._entries_if_dir_exists(self._files_dir())
    def _entries_if_dir_exists(self, path):
        return self.file_reader.entries_if_dir_exists(path)
    def for_all_files_satisfying(self, date_criteria, callable):
        for entry in self._trashinfo_entries():
            date = read_deletion_date(self.file_reader.contents_of(self._trashinfo_path(entry)))
            if(date_criteria(date)):
                file_path = self._file_path(entry)
                trashinfo_path = self._trashinfo_path(entry)
                callable(trashinfo_path, file_path)
    def _file_path(self, trashinfo_entry):
        entry=trashinfo_entry[:-len('.trashinfo')]
        path = os.path.join(self._files_dir(), entry)
        return path
    def _trashinfo_path(self, file_entry):
        return os.path.join(self.path, file_entry + '.trashinfo')
    def _files_dir(self):
        return os.path.join(os.path.dirname(self.path), 'files')
    def _trashinfo_entries(self):
        for entry in self._entries_if_dir_exists(self.path):
            if entry.endswith('.trashinfo'):
                yield entry
    def _trashinfo_path(self, entry):
        return os.path.join(self.path, entry)


def read_deletion_date(contents):
    from datetime import datetime 
    for line in contents.split('\n'):
        if line.startswith('DeletionDate='):
            return datetime.strptime(line, "DeletionDate=%Y-%m-%dT%H:%M:%S")
