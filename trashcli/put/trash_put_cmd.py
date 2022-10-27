import os

from trashcli.put.my_logger import MyLogger, LogData
from trashcli.put.parser import make_parser
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_all import TrashAll


class TrashPutCmd:
    def __init__(self,
                 trash_all,  # type: TrashAll
                 reporter,  # type: TrashPutReporter
                 ):
        self.trash_all = trash_all
        self.reporter = reporter

    def run(self, argv, environ, uid):
        program_name = os.path.basename(argv[0])
        parser = make_parser(program_name)
        try:
            options = parser.parse_args(argv[1:])
            if len(options.files) <= 0:
                parser.error("Please specify the files to trash.")
        except SystemExit as e:
            return e.code
        else:
            log_data = LogData(program_name, options.verbose)
            result = self.trash_all.trash_all(options.files,
                                              options.trashdir,
                                              options.mode,
                                              options.forced_volume,
                                              program_name,
                                              log_data,
                                              environ,
                                              uid)

            return self.reporter.exit_code(result)
