class Fs:

    @staticmethod
    def atomic_write(path, content):
        raise NotImplementedError

    @staticmethod
    def chmod(path, mode):
        raise NotImplementedError

    @staticmethod
    def isdir(path):
        raise NotImplementedError

    @staticmethod
    def isfile(path):
        raise NotImplementedError

    @staticmethod
    def getsize(path):
        raise NotImplementedError

    @staticmethod
    def exists(path):
        raise NotImplementedError

    @staticmethod
    def makedirs(path, mode):
        raise NotImplementedError

    @staticmethod
    def move(path, dest):
        raise NotImplementedError

    @staticmethod
    def remove_file(path):
        raise NotImplementedError

    @staticmethod
    def islink(path):
        raise NotImplementedError

    @staticmethod
    def has_sticky_bit(path):
        raise NotImplementedError

    @staticmethod
    def realpath(path):
        raise NotImplementedError

    @staticmethod
    def is_accessible(path):
        raise NotImplementedError

    @staticmethod
    def make_file(path, content):
        raise NotImplementedError
