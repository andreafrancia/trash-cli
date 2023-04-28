import abc

import six


@six.add_metaclass(abc.ABCMeta)
class FileSystemReaderForListCmd:
    @abc.abstractmethod
    def is_sticky_dir(self, path):  # type: (str) -> bool
        pass

    @abc.abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        pass

    @abc.abstractmethod
    def contents_of(self, path):
        pass

    @abc.abstractmethod
    def entries_if_dir_exists(self, path):
        pass

    @abc.abstractmethod
    def exists(self, path):  # type: (str) -> bool
        pass
