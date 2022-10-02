from tests.support.list_file_in_dir import list_files_in_dir


def list_files_in_subdir(path, subdir):
    return ["%s/%s" % (subdir, f) for f in list_files_in_dir(path / subdir)]
