def capture_exit_code(callable):
    try:
        callable()
    except SystemExit as e:
        return e.code
    return None
