def merge_dicts(*dicts):
    """Merges two or more dicts in a new one, the last ones win."""
    if len(dicts) < 2:
        raise TypeError("merge_dicts() needs at least two dicts, got %d" %
                        len(dicts))
    result = {}
    for d in dicts:
        result.update(d)
    return result
