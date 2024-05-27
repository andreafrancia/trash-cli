from trashcli.put.fs.script_fs import ScriptFs


class NullScriptFs(ScriptFs):
    def write_file(self, name, contents):
        pass

    def make_file_executable(self, path):
        pass
