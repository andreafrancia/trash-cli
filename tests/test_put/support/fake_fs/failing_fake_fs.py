import os.path
from tests.test_put.support.fake_fs.fake_fs import FakeFs


class FailingOnAtomicWriteFakeFs(FakeFs):
    def __init__(self):
        super(FailingOnAtomicWriteFakeFs, self).__init__()
        self._atomic_write_can_fail = False
        self._atomic_write_failure_stop = None

    def fail_atomic_create_unless(self, basename):
        self._atomic_write_can_fail = True
        self._atomic_write_failure_stop = basename

    def atomic_write(self,
                     path,
                     content):
        if self._atomic_write_is_supposed_to_fail(path):
            raise OSError("atomic_write failed")

        return super(FailingOnAtomicWriteFakeFs, self).atomic_write(path,
                                                                    content)

    def _atomic_write_is_supposed_to_fail(self,
                                          path,  # type: str
                                          ):  # type: (...) -> bool
        result = (self._atomic_write_can_fail and
                  os.path.basename(path) != self._atomic_write_failure_stop)
        return result


class FailOnMoveFakeFs(FakeFs):
    def __init__(self):
        super(FailOnMoveFakeFs, self).__init__()
        self._fail_move_on_path = None

    def move(self, src, dest):
        if src == self._fail_move_on_path:
            raise OSError("move failed")
        return super(FailOnMoveFakeFs, self).move(src, dest)

    def fail_move_on(self, path):
        self._fail_move_on_path = path


class FailingFakeFs(FailingOnAtomicWriteFakeFs,
                    FailOnMoveFakeFs):
    def __init__(self):
        super(FailingFakeFs, self).__init__()

    def assert_does_not_exist(self, path):
        if self.exists(path):
            raise AssertionError(
                "expected path to not exists but it does: %s" % path)
