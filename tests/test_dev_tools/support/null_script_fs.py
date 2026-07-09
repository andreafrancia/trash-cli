from tests.support.py2mock import Mock

from tests.support.make_scripts import ScriptFs


class NullScriptFs(ScriptFs):
    make_file_executable = Mock()
    write_file = Mock()
