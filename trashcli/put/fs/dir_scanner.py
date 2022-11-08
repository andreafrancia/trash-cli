import os


class DirScanner:
    def scandir(self, path):
        for f in DirScanner().list_all_files(path):
            yield f

    def list_all_files(self, path):
        try:
            import scandir
            walk = scandir.walk
        except ImportError:
            walk = os.walk

        for path, dirs, files in walk(path, followlinks=False):
            for f in files:
                yield os.path.join(path, f)
