try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError

MyFileNotFoundError = FileNotFoundError
