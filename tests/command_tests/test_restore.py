from unittest import TestCase
from trashcli.filesystem import Path
from trashcli.trash import HomeTrashDirectory
from nose.tools import assert_equals
from nose.tools import assert_not_equals
from nose.tools import assert_true
from nose.tools import assert_false
from nose.tools import raises
from nose import SkipTest

restore_cmd='trash-restore'
legacy_restore_cmd='restore-trash'

class CmdResult(object):
    """
    self.exit_code: integer
    self.stdout_data: string
    self.stderr_data: string
    """
    def __init__(self, exit_code, stdout_data, stderr_data):
        self.exit_code = exit_code
        self.out_data = stdout_data
        self.err_data = stderr_data

class Command(object):
    def __init__(self, cmdline, env={}):
        """
        cmdline: the command line (list of string or string)
        env: a map of enviroment variables
        """
        self.cmdline = cmdline
        if not isinstance(env, dict): 
            raise TypeError("env should be a map")
        self.env = env
    
    def run(self,input_=None):
        """
        Execute the command in the current enviroment and return the CmdResult
        """
        from subprocess import Popen
        from subprocess import PIPE
        proc = Popen(self.cmdline, 
                     stdin=PIPE, 
                     stdout=PIPE, 
                     stderr=PIPE, 
                     env=self.env)
        (stdout_data,stderr_data) = proc.communicate(input_)
        proc.wait()
        return CmdResult(proc.returncode, stdout_data, stderr_data)

    def assert_succeed(self, input=None):
        result=self.run(input)
        if result.exit_code != 0:
            print 'command failed: %s' % str(self.cmdline)
            print 'exit_code=', result.exit_code
            print 'err_data=', result.err_data
            print 'out_data=', result.out_data
            raise AssertionError("The command returns a %s code instead of 0" 
                                 % result.exit_code)
        return result

    def assert_fail(self, input=None):
        result=self.run(input)
        if result.exit_code == 0:
            raise AssertionError("The command returns a 0 exit code instead, "
                                 "while non zero status is expected")
        return result
    
class CommandTest(TestCase):
    def test_run_retuns_exit_code(self):
        result=Command("/bin/false").run()
        assert_not_equals(0, result.exit_code)
        
        result=Command("/bin/true").run()
        assert_equals(0, result.exit_code)
    
    def test_run_returns_output(self):
        result=Command(["/bin/echo", "foo"]).run()
        assert_equals("foo\n", result.out_data)
        
        result=Command(["/bin/echo", "-n", "foo"]).run()
        assert_equals("foo", result.out_data)

    def test_run_returns_error_messages(self):
        result=Command(["python", "--bad-option"]).run()
        assert_true(result.err_data.startswith("Unknown option: --"), 
                    "This may fail even if the code works")
    
    def test_run_reads_the_input(self):
        result=Command("cat").run("text")
        assert_equals("text", result.out_data)
    
    def test_run_honors_env(self):
        result=Command("/usr/bin/env",{'VAR':'value'}).run()
        assert_equals('VAR=value\n', result.out_data)
    
    def test_env_empty_by_default(self):
        result=Command("/usr/bin/env").run()
        assert_equals('', result.out_data)

    @raises(TypeError)
    def test_mistake_is_detected(self):
        Command("/bin/ls", "-l") # <-- mistake, correct --> Command(["ls","-l"])
        
# Peraphs TODO: Refactoring: move cmd(), create_file(), trash(), trash-dir to 
# a Sandbox class.
class RestoreTest(TestCase):
    def cmd(self, *cmdline) :
        """
        Create a command with the current enviroment (self.env)
        """
        return Command(cmdline, self.env)
    
    def setUp(self):
        self.sandbox = Path("./sandbox")
        self.sandbox.remove()
        self.sandbox.mkdirs()
        self.env = {
            'HOME':'./sandbox/home',
        }
        self.trashdir = HomeTrashDirectory(
            Path('./sandbox/home/.local/share/Trash'))
    
    def create_file(self, path, content=None):
        """
        Create a file in sandbox with content
        """
        file=self.sandbox.join(path)
        file.touch()
        if content!=None :
            file.write_file(content)
            
        return file

    def trash(self, path):
        """
        Trash the file in the trash dir at sandbox/home/.local/share/Trash
        """
        result = self.trashdir.trash(path)
        
        # sanity check 
        assert not path.exists()
        return result
    
    def test_cmd_creates_commands(self):
        result = self.cmd("echo", "pippo").run()
        assert_equals("",result.err_data)
        assert_equals("pippo\n", result.out_data)
        assert_equals(0,result.exit_code)
    
    def test_version_option(self):
        """
        $ trash-restore --version
        0.2.1
        """
        import re
        result = self.cmd(restore_cmd,'--version').assert_succeed()
        assert_equals("", result.err_data)
        expected = re.compile("trash-restore (\d)+\.(\d)+\.(\d)+")
        assert expected.match(result.out_data) is not None
    
    def test_restore_restores_trashed_file_absolute(self):
        from time import sleep
        """
        $ trash-list
        2009-01-12 12:00:00 /home/andrea/file
        1977-01-12 12:00:00 /home/andrea/file
        $ trash-restore /home/andrea/file # restore the latest trashed one
        $ trash-list
        1977-01-12 12:00:00 /home/andrea/file # the oldest remain in trashcan
        """
        
        # prepare
        foo_file = self.create_file('foo', "first")
        trashed_file1 = self.trash(foo_file)
        
        sleep(1) # to make sure that deletion dates differs
        foo_file = self.create_file('foo', "second")
        trashed_file2 = self.trash(foo_file)

        sleep(1) # to make sure that deletion dates differs
        foo_file = self.create_file('foo', "latest")
        trashed_file3 = self.trash(foo_file)
        assert_false(foo_file.exists())
        
        print trashed_file1.deletion_date
        print trashed_file2.deletion_date
        print trashed_file3.deletion_date
        
        # execute 
        self.cmd(restore_cmd,foo_file.absolute()).assert_succeed()
        assert_true(foo_file.exists()) # File has been restored ?
        assert_equals("latest", foo_file.read()) # Is the latest deleted file?
    
    def test_restores_with_relative_name(self):
        """
        $ trash-list
        2009-01-12 12:00:00 /home/andrea/file
        $ cd /home/andrea
        $ trash-restore ./file
        """
        # prepare
        foo_file = self.create_file('file', "content")
        self.trash(foo_file)
        assert_false(foo_file.exists())
        
        # execute 
        self.cmd(restore_cmd,"./sandbox/file").assert_succeed()
        assert_true(foo_file.exists()) # File has been restored ?
        assert_equals("content", foo_file.read()) # Is the latest deleted file?

    def test_trashed_file_does_not_found(self):
        """
        $ trash-restore non-existent
        trash-restore: cannot restore path `non-existent': "
                      "Not found in any trash directory.
        """
        raise SkipTest()
        # execute
        result = self.cmd(restore_cmd, 'non-existent').assert_fail()
        # test
        assert_equals(result.exit_code, 1)
        assert_equals(result.out_data, "")
        assert_equals(result.err_data, 
                      "trash-restore: cannot restore path `non-existent': "
                      "Not found in any trash directory.")
    
    def test_overwrite_attempt(self):
        """
        $ touch file
        $ trash-restore file
        trash-restore: cannot overwrite `file': File exists.
        """
        raise SkipTest()
        # prepare
        self.create_file('existing-file')
        self.trash('existing-file')
        self.create_file('existing-file')
        
        # execute
        result = self.cmd(restore_cmd, 'existing-file').assert_fail()
        
        # test
        assert_equals(result.exit_code, 1)
        assert_equals(result.out_data, "")
        assert_equals(result.err_data, 
                      "trash-restore: cannot overwrite`existing-file': "
                      "File exists.")
    
    def test_overwrite_attempt_with_force_option(self):
        """
        $ touch file
        $ trash-restore --force file     #succeed
        """
        raise SkipTest()
        # prepare
        self.create_file('existing-file')
        self.trash('existing-file')
        self.create_file('existing-file')
        
        # execute
        result = self.cmd(restore_cmd, '--force', 
                          'existing-file').assert_succeed
        
        # test
        assert_equals(result.exit_code, 0)
        assert_equals(result.out_data, "")
        assert_equals(result.err_data, "")
        
    
    def test_help_option(self):
        """
        $ trash-restore --help 
        Usage: trash-restore ...
        ...
        """
        raise SkipTest()
        result = self.cmd(restore_cmd, '--help').assert_succeed()
        assert_equals(result.exit_code, 0)
        assert_equals(result.out_data, 
"""Usage: trash-restore TRASHED-FILE [NEW-LOCATION]
Restore the TRASHED-FILE to its original location or to NEW-LOCATION.

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -f, --force          force overwrite
  -v, --verbose        explain what is being done
""")
        assert_equals(result.err_data, "")
        
    def test_issue_19(self):
        # bug: http://code.google.com/p/trash-cli/issues/detail?id=19
        # also reported in: 
        #     https://bugs.launchpad.net/ubuntu/+source/trash-cli/+bug/310088
        
        self.sandbox.join('dir').mkdir()
        self.sandbox.join("dir/file").touch()
        
        self.trash(Path('sandbox/dir/file'))
        self.sandbox.join('dir').remove()
        
        result = self.cmd(legacy_restore_cmd).assert_succeed("0")
        assert result.err_data == ""
        print result.out_data
        assert result.exit_code == 0
        assert self.sandbox.join("dir").join("file").exists()
        