import unittest

from subprocess import PIPE, Popen
import sys

class TestScriptsSmoke(unittest.TestCase):
    def test_trash_rm_works(self):
        self.run_script('trash-rm')
        assert "Usage:" in self.stderr.splitlines()

    def test_trash_put_works(self):
        self.run_script('trash-put')
        assert ("Usage: trash-put [OPTION]... FILE..." in
                self.stderr.splitlines())

    def test_trash_put_touch_filesystem(self):
        self.run_script('trash-put', 'non-existent')
        assert ("trash-put: cannot trash non existent 'non-existent'\n" ==
                     self.stderr)

    def run_script(self, script, *args):
        process = Popen([sys.executable, script] + list(args),
                    env={'PYTHONPATH':'.'},
                    stdin=None,
                    stdout=PIPE,
                    stderr=PIPE)

        (self.stdout, self.stderr) = process.communicate()
        self.stderr = self.stderr.decode('utf-8')
        process.wait()
        self.returncode = process.returncode


