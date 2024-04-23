from typing import List
from typing import Optional

from tests.support.run.run_command import run_command
from tests.support.dirs.my_path import MyPath
from tests.test_put.test_e2e.run_trash_put.put_result import PutResult
from tests.test_put.test_e2e.run_trash_put.put_result import make_put_result
from tests.test_put.test_e2e.run_trash_put.stream import Stream
from trashcli.lib.environ import Environ


def run_trash_put(tmp_dir,  # type: MyPath
                  args,  # type: List[str]
                  env=None,  # type: Optional[Environ]
                  ):  # type: (...) -> PutResult
    env = env or {}
    root_dir = tmp_dir
    cur_dir = tmp_dir
    trash_dir = tmp_dir / 'trash-dir'
    return run_trash_put4(root_dir, cur_dir, trash_dir, args, env)


def run_trash_put3(cur_dir,  # type: MyPath
                   trash_dir,  # type: MyPath
                   args,  # type: List[str]
                   ):  # type: (...) -> PutResult
    return run_trash_put4(cur_dir, cur_dir, trash_dir, args, env={})


def run_trash_put4(root_dir,  # type: MyPath
                   cur_dir,  # type: MyPath
                   trash_dir,  # type: MyPath
                   args,  # type: List[str]
                   env,  # type: Environ
                   ):  # type: (...) -> PutResult
    extra_args = [
        '-v',
        '--trash-dir', trash_dir,
    ]
    args = extra_args + args
    return run_trash_put23(root_dir,
                           cur_dir,
                           args,
                           env)


def run_trashput_with_vol(temp_dir,  # type: MyPath
                          fake_vol,  # type: MyPath
                          args,  # type: List[str]
                          ):  # type: (...) -> Stream
    result = run_trash_put2(temp_dir,
                            ["--force-volume=%s" % fake_vol, '-v'] + args,
                            env=with_uid(123))
    output = result.both().replace(fake_vol, "/vol")
    return output


def run_trash_put2(cur_dir,  # type: MyPath
                   args,  # type: List[str]
                   env,  # type: Environ
                   ):  # type: (...) -> PutResult

    return run_trash_put23(cur_dir, cur_dir, args, env)


def run_trash_put23(root_dir,  # type: MyPath
                    cur_dir,  # type: MyPath
                    args,  # type: List[str]
                    env,  # type: Environ
                    ):  # type: (...) -> PutResult

    result = run_command(cur_dir, 'trash-put',
                         args, env=env)

    return make_put_result(result, root_dir)


def with_uid(uid):
    return {'TRASH_PUT_FAKE_UID_FOR_TESTING': str(uid)}
