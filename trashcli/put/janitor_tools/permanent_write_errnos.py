# Errors that retrying with another suffix in the same directory can never fix.
def _get_permanent_write_errnos():
    """
    Get the list of errors that retrying with another suffix in the same
    directory can never fix.
    """
    import errno
    errors_names = ['EACCES', 'EPERM', 'ENOSPC', 'EDQUOT', 'EROFS']
    errno_available = [getattr(errno, name, None) for name in errors_names]
    errno_with_removed_none = [code for code in errno_available if code is not None]
    return errno_with_removed_none


HARD_ERRNOS = _get_permanent_write_errnos()
