import re


class VersionSaver:
    def __init__(self, fs):
        self.fs = fs

    def save_new_version(self, new_version, path):
        content = self.fs.read_text(path)
        new_content = re.sub(r'^version(\s*)=.*',
                             'version = \'%s\'' % new_version,
                             content,
                             flags=re.MULTILINE)
        self.fs.make_text_file(path, new_content)
