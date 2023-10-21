from typing import List

from trashcli.lib.environ import Environ
from trashcli.put.my_logger import LogData
from trashcli.put.parser import Parser, ExitWithCode, Trash
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_all import TrashAll


class TrashPutCmd:
    def __init__(self,
                 trash_all,  # type: TrashAll
                 reporter,  # type: TrashPutReporter
                 ):
        self.trash_all = trash_all
        self.reporter = reporter

    def run_put(self,
                argv,  # type: List[str]
                environ,  # type: Environ
                uid,  # type: int
                ):  # type: (...) -> int
        parser = Parser()
        parsed = parser.parse_args(argv)
        if isinstance(parsed, ExitWithCode):
            return parsed.exit_code
        elif isinstance(parsed, Trash):
            program_name = parsed.program_name
            log_data = LogData(program_name, parsed.verbose)
            result = self.trash_all.trash_all(parsed.files,
                                              parsed.trash_dir,
                                              parsed.mode,
                                              parsed.forced_volume,
                                              parsed.home_fallback,
                                              program_name,
                                              log_data,
                                              environ,
                                              uid)

            return self.reporter.exit_code(result)
