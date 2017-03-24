import os, shutil, errno

class FileSystemListing:
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            try:
                for entry in os.listdir(path):
                    yield entry
            except OSError:
                pass
    def exists(self, path):
        return os.path.exists(path)

class FileSystemReader(FileSystemListing):
    def is_sticky_dir(self, path):
        return os.path.isdir(path) and has_sticky_bit(path)
    def is_symlink(self, path):
        return os.path.islink(path)
    def contents_of(self, path):
        return open(path).read()

class FileRemover:
    def remove_file(self, path):
        try:
            return os.remove(path)
        except OSError as e:
            if e.errno == errno.EISDIR:
                pass
            else:
                return
        try:
            return shutil.rmtree(path)
        except OSError:
            pass
    def remove_file_if_exists(self,path):
        if os.path.exists(path): self.remove_file(path)

def contents_of(path): # TODO remove
    return FileSystemReader().contents_of(path)
def has_sticky_bit(path): # TODO move to FileSystemReader
    import stat
    return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX

def remove_file(path):
    if(os.path.lexists(path)):
        try:
            os.remove(path)
        except OSError as e:
            if e.errno == errno.EISDIR:
                pass
            else:
                return

        try:
            shutil.rmtree(path)
        except OSError:
            pass

def move(path, dest) :
    return shutil.move(path, str(dest))

def list_files_in_dir(path):
    for entry in os.listdir(path):
        result = os.path.join(path, entry)
        yield result

def mkdirs(path):
    if os.path.isdir(path):
        return
    os.makedirs(path)

def atomic_write(filename, content):
    file_handle = os.open(filename, os.O_RDWR | os.O_CREAT | os.O_EXCL,
            0o600)
    os.write(file_handle, content)
    os.close(file_handle)

def ensure_dir(path, mode):
    if os.path.isdir(path):
        os.chmod(path, mode)
        return
    os.makedirs(path, mode)
