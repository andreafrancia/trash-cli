# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import Iterator
from typing import List, Tuple
from typing import NamedTuple

from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.environ import Environ
from trashcli.lib.trash_dirs import home_trash_dir
from trashcli.lib.trash_dirs import volume_trash_dir1
from trashcli.lib.trash_dirs import volume_trash_dir2
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.check_type import CheckType
from trashcli.put.core.check_type import NoCheck
from trashcli.put.core.check_type import TopTrashDirCheck
from trashcli.put.core.path_maker_type import PathMakerType
from trashcli.put.gate import Gate

class TrashDirectoriesFinder:
    def __init__(self,
                 fs,  # type: VolumeOf
                 ):
        self.fs = fs

    def possible_trash_directories_for(self,
                                       volume,  # type: str
                                       specific_trash_dir,  # type: str
                                       environ,  # type: Environ
                                       uid,  # type: int
                                       home_fallback,  # type: bool
                                       ):  # type: (...) -> Iterator[Candidate]
        conf = _Conf(specific_trash_dir, home_fallback, self.fs)

        for possible_candidate in self._enumerate_trash_dirs(conf, uid, volume,
                                                             environ):
            if possible_candidate.is_to_be_used:
                yield possible_candidate.candidate

    def _enumerate_trash_dirs(self,
                             conf,  # type: _Conf
                             uid,  # type: int
                             volume,  # type: str
                             environ,  # type: Environ
                             ):
        use_specific = conf.use_user_trah_dir()
        use_standard = conf.use_standard()
        use_home_fallback = conf.use_home_fallback()
        P = PossibleCandidate
        for path, dir_volume in conf.user_trash_dirs():
            yield P(use_specific, _make_user_dir(path, dir_volume))
        for path, dir_volume in home_trash_dir(environ, self.fs):
            yield P(use_standard, _make_home_trash_dir(path, dir_volume))
        for path, dir_volume in volume_trash_dir1(volume, uid):
            yield P(use_standard, _make_top_dir(path, dir_volume))
        for path, dir_volume in volume_trash_dir2(volume, uid):
            yield P(use_standard, _make_alt_top_dir(path, dir_volume))
        for path, dir_volume in home_trash_dir(environ, self.fs):
            yield P(use_home_fallback, _make_fallback_dir(path, dir_volume))


class _Conf:
    def __init__(self,
                 specific_trash_dir,  # type: str
                 home_fallback,  # type: bool
                 fs,  # type: VolumeOf
                 ):
        self.specific_trash_dir = specific_trash_dir
        self.home_fallback = home_fallback
        self.fs = fs

    def use_user_trah_dir(self):  # type: (...) -> bool
        return self.specific_trash_dir is not None

    def user_trash_dirs(self):  # type: (...) -> List[Tuple[str, str]]
        if not self.use_user_trah_dir():
            return []

        return [(self.specific_trash_dir,
                 self.fs.volume_of(self.specific_trash_dir))]

    def use_standard(self):  # type: (...) -> bool
        return not self.use_user_trah_dir()

    def use_home_fallback(self):  # type: (...) -> bool
        return (self.home_fallback and
                not self.use_user_trah_dir())


class PossibleCandidate(NamedTuple("Prova", [
    ('is_to_be_used', bool),
    ('candidate', Candidate),
])):
    pass

AbsolutePaths = PathMakerType.AbsolutePaths
RelativePaths = PathMakerType.RelativePaths
SameVolume = Gate.SameVolume
HomeFallback = Gate.HomeFallback


def _make_user_dir(path,  # type: str
                   volume_dir,  # type: str
                   ):  # type: (...) -> Candidate
    return _make_candidate(path, volume_dir,
                           RelativePaths, NoCheck, SameVolume)


def _make_home_trash_dir(path,  # type: str
                         volume_dir,  # type: str
                         ):
    return _make_candidate(path, volume_dir,
                           AbsolutePaths, NoCheck, SameVolume)


def _make_fallback_dir(path,  # type: str
                       dir_volume,  # type: str
                       ):
    return _make_candidate(path, dir_volume,
                           AbsolutePaths, NoCheck, HomeFallback)


def _make_top_dir(path,  # type: str
                  dir_volume,  # type: str
                  ):
    return _make_candidate(path, dir_volume,
                           RelativePaths, TopTrashDirCheck, SameVolume)


def _make_alt_top_dir(path,  # type: str
                      dir_volume,  # type: str
                      ):
    return _make_candidate(path, dir_volume,
                           RelativePaths, NoCheck, SameVolume)

def _make_candidate(path,  # type: str
                    volume,  # type: str
                    path_maker_type,  # type:  PathMakerType
                    check_type,  # type: CheckType
                    gate,  # type: Gate
                    ):  # type: (...) -> Candidate
    return Candidate(trash_dir_path=path,
                     volume=volume,
                     path_maker_type=path_maker_type,
                     check_type=check_type,
                     gate=gate)
