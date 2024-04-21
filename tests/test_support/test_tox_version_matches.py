import os
import sys


def test_tox_version_matched():
    env_name = os.getenv('TOX_ENV_NAME', None)
    version = sys.version_info

    assert (env_name, version.major, version.minor) in [
        ('py27', 2, 7),
        ('py310', 3, 10),
        (None, version.major, version.minor)
    ]