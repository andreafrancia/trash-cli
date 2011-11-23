import os

class FileSystem:
    def contents_of(self, path):
        return file(path).read()
    def remove_file(self, path):
        return os.remove(path)
    def remove_file_if_exists(self,path):
        if self.exists(path): self.remove_file(path)
    def exists(self, path):
        return os.path.exists(path)
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry

from .list_mount_points import mount_points

class EmptyCmd():
    from datetime import datetime
    def __init__(self, out, err, environ, now = datetime.now, fs =
                 FileSystem(), list_volumes=mount_points, getuid=os.getuid):
        self.out          = out
        self.err          = err
        self.now          = now
        self.fs           = fs
        self.infodirs     = InfoDirs(environ, getuid, list_volumes)
    def run(self, *argv):
        if len(argv) > 1:
            date_criteria = OlderThan(int(argv[1]), self.now)
        else:
            date_criteria = always

        janitor = Janitor(self.fs, date_criteria)
        self.infodirs.for_each_path(janitor)
class Janitor:
    def __init__(self, fs, date_criteria):
        self.fs = fs
        self.date_criteria = date_criteria
    def __call__(self, info_dir_path):
        infodir = InfoDir(self.fs, info_dir_path)
        infodir.remove_all_files_satisfying(self.date_criteria)
        infodir.remove_all_files()
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
            yield '%(volume)s/Trash/%(uid)s/info' % { 'volume': volume, 'uid': self.getuid()}
            yield '%(volume)s/Trash-%(uid)s/info' % { 'volume': volume, 'uid': self.getuid()}
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
class BothRemover:
    def __init__(self, fs):
        self.fs = fs
    def __call__(self, trashinfo_path, file_path):
        self.fs.remove_file_if_exists(file_path)
        self.fs.remove_file(trashinfo_path)
class InfoDir:
    def __init__(self, fs, path):
        self.path = path
        self.fs = fs
    def for_all_orphan(self, callable):
        for entry in self._files():
            trashinfo_path = self._trashinfo_path(entry)
            file_path = os.path.join(self._files_dir(), entry)
            if not self.fs.exists(trashinfo_path): callable(file_path)
    def remove_all_files(self):
        for entry in self._files():
            self._remove_file(entry)
    def _deletion_date(self, entry):
        return read_deletion_date(self.fs.contents_of(self._trashinfo_path(entry)))
    def _files(self):
        return self._entries_if_dir_exists(self._files_dir())
    def _entries_if_dir_exists(self, path):
        return self.fs.entries_if_dir_exists(path)
    def remove_all_files_satisfying(self, date_criteria):
        remover=BothRemover(self.fs)
        self.for_all_files_satisfying(date_criteria, remover)
    def for_all_files_satisfying(self, date_criteria, callable):
        for entry in self._trashinfo_entries():
            date = read_deletion_date(self.fs.contents_of(self._trashinfo_path(entry)))
            if(date_criteria(date)):
                file_path = self._file_path(entry)
                trashinfo_path = self._trashinfo_path(entry)
                callable(trashinfo_path, file_path)
    def _remove_file(self, entry):
        self.fs.remove_file(os.path.join(self._files_dir(), entry))
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
