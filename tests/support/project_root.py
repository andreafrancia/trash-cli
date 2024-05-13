import os


def project_root():
    this_file = os.path.realpath(__file__)
    support_dir = os.path.dirname(this_file)
    tests_dir = os.path.dirname(support_dir)
    return os.path.dirname(tests_dir)
