import os


def remove_dir_if_exists(dir):
    if os.path.exists(dir):
        os.rmdir(dir)
