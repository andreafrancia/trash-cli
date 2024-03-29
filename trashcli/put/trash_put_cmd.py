from typing import List

from trashcli.lib.environ import Environ
from trashcli.put.context import Context
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
            context = Context(paths=parsed.files,
                              user_trash_dir=parsed.trash_dir,
                              mode=parsed.mode,
                              forced_volume=parsed.forced_volume,
                              home_fallback=parsed.home_fallback,
                              program_name=program_name,
                              log_data=log_data,
                              environ=environ,
                              uid=uid)
            result = self.trash_all.trash_all(context)

            return self.reporter.exit_code(result)
