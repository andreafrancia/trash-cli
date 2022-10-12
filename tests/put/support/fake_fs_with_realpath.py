class FakeFsWithRealpath:
    @staticmethod
    def realpath(path):
        return path
