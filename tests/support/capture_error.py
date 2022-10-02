def capture_error(callable):
    try:
        callable()
    except Exception as e:
        return e
    return None
