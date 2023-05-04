# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import

import os

from trashcli.fstab.volume_of import VolumeOf


def home_trash_dir_path_from_env(environ):
    if 'XDG_DATA_HOME' in environ:
        return ['%(XDG_DATA_HOME)s/Trash' % environ]
    elif 'HOME' in environ:
        return ['%(HOME)s/.local/share/Trash' % environ]
    return []


def home_trash_dir_path_from_home(home_dir):
    return '%s/.local/share/Trash' % home_dir


def home_trash_dir(environ,
                   volume_of,  # type: VolumeOf
                   ):
    paths = home_trash_dir_path_from_env(environ)
    for path in paths:
        yield path, volume_of.volume_of(path)


def volume_trash_dir1(volume, uid):
    path = os.path.join(volume, '.Trash/%s' % uid)
    yield path, volume


def volume_trash_dir2(volume, uid):
    path = os.path.join(volume, ".Trash-%s" % uid)
    yield path, volume
