from typing import NamedTuple, Any, Optional, Union


class ResultWithExitCode(NamedTuple('ResultWithExitCode', [
    ('result', Any), ('exit_code', Optional[Union[int, str]])])):
    pass
