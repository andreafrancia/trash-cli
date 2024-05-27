import os


class Path(str):
    def __new__(cls, path):
        return super(Path, cls).__new__(cls, path)

    def __init__(self,
                 path,  # type: str
                 ):  # type: (...) -> None
        self.path = path

    def __truediv__(self, other_path):
        return self.path_join(other_path)

    def __div__(self, other_path):
        return self.path_join(other_path)

    def path_join(self, other_path):
        return type(self)(os.path.join(self, other_path))
