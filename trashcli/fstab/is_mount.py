import os


class RealIsMount:
    def is_mount(self, path):
        return os.path.ismount(path)
