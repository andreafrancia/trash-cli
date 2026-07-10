from typing import Any, Callable

from tests.support.cmd.result_with_exit_code import ResultWithExitCode


def capture_exit_code2(
        cmd, # type: Callable[[], Any]
):  # type: (...) -> ResultWithExitCode
    try:
        result = cmd()
        return ResultWithExitCode(result, None)
    except SystemExit as e:
        return ResultWithExitCode(None, e.code)
