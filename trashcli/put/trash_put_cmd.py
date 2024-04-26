from typing import List

from trashcli.lib.environ import Environ
from trashcli.put.context import Context
from trashcli.put.my_logger import LogData
from trashcli.put.parser import ExitWithCode
from trashcli.put.parser import Parser
from trashcli.put.parser import Trash
from trashcli.put.reporting.trash_put_reporter import TrashPutReporter
from trashcli.put.trasher import Trasher


class TrashPutCmd:
    def __init__(self,
                 reporter,  # type: TrashPutReporter
                 trasher,  # type: Trasher
                 ):
        self.reporter = reporter
        self.trasher = trasher

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
            result = context.trash_each(self.trasher)

            return self.reporter.exit_code(result)
