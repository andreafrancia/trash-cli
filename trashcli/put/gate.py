import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Gate:
    @abc.abstractmethod
    def can_trash_in(self, trashee, candidate, trash_dir_volume):
        pass
