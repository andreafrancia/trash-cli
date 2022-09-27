import os


class Access:
    @staticmethod
    def is_accessible(path):
        return os.access(path, os.F_OK)
