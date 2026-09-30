from abc import abstractmethod

from trashcli.compat import Protocol


# NOTE: despite its name this is NOT a real implementation, it is a protocol.
# "Real" here is part of "realpath": the class describes the file systems that
# can compute os.path.realpath() of a path, real or fake.
class RealPathFs(Protocol):
    @abstractmethod
    def realpath(self, path):
        raise NotImplementedError
