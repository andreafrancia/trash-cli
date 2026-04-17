import os


def is_input_interactive():
    return os.isatty(0)
