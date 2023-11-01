import os
from typing import NamedTuple

from trashcli.put.clock import PutClock
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.either import Either, Right, Left
from trashcli.put.core.failure_reason import FailureReason
from trashcli.put.core.failure_reason import LogContext
from trashcli.put.format_trash_info import format_trashinfo
from trashcli.put.janitor_tools.info_file_persister import InfoFilePersister
from trashcli.put.janitor_tools.info_file_persister import TrashinfoData
from trashcli.put.original_location import OriginalLocation


class UnableToCreateTrashInfoContent(
    NamedTuple('UnableToCreateTrashInfoContent', [
        ('error', Exception),
    ]), FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> str
        return "failed to generate trashinfo content: %s" % (
            self.error)


class TrashInfoCreator:
    def __init__(self,
                 persister,  # type: InfoFilePersister
                 original_location,  # type: OriginalLocation
                 clock,  # type: PutClock
                 ):
        self.original_location = original_location
        self.clock = clock

    Result = Either[TrashinfoData, UnableToCreateTrashInfoContent]

    def make_trashinfo_data(self,
                            path,  # type: str
                            candidate,  # type: Candidate
                            ):  # type: (...) -> Result
        try:
            original_location = self.original_location.for_file(path,
                                                                candidate.path_maker_type,
                                                                candidate.volume)
            content = format_trashinfo(original_location, self.clock.now())
            basename = os.path.basename(original_location)
            trash_info_data = TrashinfoData(basename, content,
                                            candidate.info_dir())
            return Right(trash_info_data)
        except (IOError, OSError) as error:
            return Left(UnableToCreateTrashInfoContent(error))
