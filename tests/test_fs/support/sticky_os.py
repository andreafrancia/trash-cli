import subprocess


def make_it_sticky_with_chmod(path):
    subprocess.check_call(["chmod", "1777", path])


def make_it_not_sticky_with_chmod(path):
    subprocess.check_call(["chmod", "0777", path])


def read_stickiness_from_ls_ld_output(path):
    ret = subprocess.check_output(["ls", "-ld", path])
    return ret.decode("ascii")[9]
