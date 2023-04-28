from __future__ import absolute_import

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class DirReader:
    @abc.abstractmethod
    def entries_if_dir_exists(self, path):  # type: (str) -> list[str]
        raise NotImplementedError()

    @abc.abstractmethod
    def exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()
