def octal(n):  # type: (int) -> str
    return "%s%s" % ("0o", _remove_octal_prefix(oct(n)))


def _remove_octal_prefix(o):
    if o.startswith('0o'):
        return o[2:]
    elif o.startswith('0'):
        return o[1:]
    else:
        ValueError('Invalid octal format: %s' % o)
