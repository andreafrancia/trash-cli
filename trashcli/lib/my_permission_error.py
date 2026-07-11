from typing import Type


def get_permission_error_class():  # type: () -> Type[Exception]
    """
    PermissionError is builtin exception introduced in Python from 3.3 (by PEP
    3151). This function provide the compatibility layer for using the right
    exception depending on the current python version.
    Rif: https://peps.python.org/pep-3151/
    """
    try:
        # To check a builtin is present we just need reference it by name.
        # The line below contains the "type: ignore" comment in order to make
        # mypy happy even the current python versions is before the version of
        # introduction (python version 3.3).
        return PermissionError  # type: ignore
    except NameError:
        # I don't remember how I decided to return OSError, maybe I've done some
        # experiments with Python 2.7 to check which exception is raised when I
        # added a file or a directory of which I didn't have the permissions.
        return OSError


MyPermissionError = get_permission_error_class()
