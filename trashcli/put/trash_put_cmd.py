import os

from trashcli.put.trash_all import TrashAll
from trashcli.put.my_logger import MyLogger
from trashcli.put.parser import make_parser
from trashcli.put.reporter import TrashPutReporter


class TrashPutCmd:
    def __init__(self, stderr, trasher):
        self.stderr = stderr
        self.trasher = trasher

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
            logger = MyLogger(self.stderr, program_name, options.verbose)
            reporter = TrashPutReporter(logger, environ)
            trash_all = TrashAll(logger, self.trasher, reporter)
            result = trash_all.trash_all(options.files,
                                         options.trashdir,
                                         options.mode,
                                         options.forced_volume,
                                         program_name,
                                         environ,
                                         uid)

            return reporter.exit_code(result)
