import os


def list_files_in_dir(path):
    if not os.path.isdir(path):
        return []
    return os.listdir(path)
