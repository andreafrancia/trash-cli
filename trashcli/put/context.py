from typing import List
from typing import NamedTuple
from typing import Optional

from trashcli.lib.environ import Environ
from trashcli.put.core.logs import LogData
from trashcli.put.core.mode import Mode


class Context(NamedTuple('Context', [
    ('paths', List[str]),
    ('user_trash_dir', Optional[str]),
    ('mode', Mode),
    ('forced_volume', Optional[str]),
    ('home_fallback', bool),
    ('program_name', str),
    ('log_data', LogData),
    ('environ', Environ),
    ('uid', int),
])):
    pass
