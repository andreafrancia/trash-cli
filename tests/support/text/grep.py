def grep(stream, pattern):  # type: (str, str) -> str
    return ''.join([line
                    for line in stream.splitlines(True)
                    if pattern in line])
