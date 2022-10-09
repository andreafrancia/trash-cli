try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

MyFileNotFoundError = FileNotFoundError
