import os

from typing import Mapping

Environ = Mapping[str, str]


def cast_environ(env,
                 ):  # type: (...) -> Environ
    if env == os.environ:
        return env
    else:
        raise ValueError("env must be os.environ")
