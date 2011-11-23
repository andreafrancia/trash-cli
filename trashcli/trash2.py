import os

class FileSystem:
    def contents_of(self, path):
        return file(path).read()
    def remove_file(self, path):
        return os.remove(path)
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
        self.fs           = FileSystem()
        self.infodirs     = InfoDirs(environ, getuid, list_volumes)
    def run(self, *argv):
        if len(argv) > 1:
            date_criteria = OlderThan(int(argv[1]), self.now)
        else:
            date_criteria = always

        self._empty_trashcans_according_to(date_criteria)
    def _empty_trashcans_according_to(self, date_criteria):
        for infodir in self._info_dirs():
            for entry in infodir.trashinfo_entries():
                infodir.remove_both(entry, date_criteria)
            for entry in infodir.files():
                infodir.remove_file(entry)
    def _info_dirs(self):
        for path in self.infodirs.paths():
            yield InfoDir(self.fs, path)

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

def info_dirs_paths(environ):
    return InfoDirs(environ).paths()
def always(deletion_date): return True
class OlderThan:
    def __init__(self, days_ago, now):
        from datetime import timedelta
        self.limit_date = now() - timedelta(days=days_ago)
    def __call__(self, deletion_date):
        return deletion_date < self.limit_date
class InfoDir:
    def __init__(self, fs, path):
        self.path = path
        self.fs = fs
    def files_dir(self):
        return os.path.join(os.path.dirname(self.path), 'files')
    def trashinfo_entries(self):
        for entry in self._entries_if_dir_exists(self.path):
            if entry.endswith('.trashinfo'):
                yield entry
    def trashinfo_path(self, entry):
        return os.path.join(self.path, entry)
    def remove_trashinfo(self, entry):
        self.fs.remove_file(self.trashinfo_path(entry))
    def remove_file_if_exists(self, trashinfo_entry):
        path = self.file_path(trashinfo_entry)
        if self.fs.exists(path): self.fs.remove_file(path)
    def file_path(self, trashinfo_entry):
        entry=trashinfo_entry[:-len('.trashinfo')]
        path = os.path.join(self.files_dir(), entry)
        return path
    def remove_file(self, entry):
        self.fs.remove_file(os.path.join(self.files_dir(), entry))
    def files(self):
        return self._entries_if_dir_exists(self.files_dir())
    def _entries_if_dir_exists(self, path):
        return self.fs.entries_if_dir_exists(path)
    def remove_both(self, entry, criteria=always):
        date = read_deletion_date(self.fs.contents_of(self.trashinfo_path(entry)))
        if(criteria(date)):
            self.remove_file_if_exists(entry)
            self.remove_trashinfo(entry)
    def _deletion_date(self, entry):
        return read_deletion_date(self.fs.contents_of(self.trashinfo_path(entry)))
def read_deletion_date(contents):
    from datetime import datetime 
    for line in contents.split('\n'):
        if line.startswith('DeletionDate='):
            return datetime.strptime(line, "DeletionDate=%Y-%m-%dT%H:%M:%S")
