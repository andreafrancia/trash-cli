from typing import Type


def get_permission_error_class():  # type: () -> Type[Exception]
    try:
        return PermissionError  # type: ignore
    except NameError:
        return OSError


MyPermissionError = get_permission_error_class()
