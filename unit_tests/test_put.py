from nose.tools import assert_equals
from unittest import TestCase
from StringIO import StringIO
from trashcli.cli.put import TrashPutCmd

class TrashPutCmd_Test(TestCase):

    def test_should_skip_dot_entry(self):
	self.when_called_with_arg('.')
	self.stderr_should_be("trash-put: cannot trash directory `.'\n")
    
    def test_should_skip_dotdot_entry(self):
	self.when_called_with_arg('..')
	self.stderr_should_be("trash-put: cannot trash directory `..'\n")

    def when_called_with_arg(self, arg):
	args=['trash-put', arg]
	cmd=TrashPutCmd(self.stdout, self.stderr)
	main_function = lambda:cmd.run(args)
	self.detect_and_save_exit_code(main_function)

    def detect_and_save_exit_code(self,main_function):
	self.actual_exit_code=0
	try:
	    result=main_function()
	    if result is not None:
		self.actual_exit_code=result
	except SystemExit, e:
	    self.actual_exit_code=e.code

    def stderr_should_be(self, expected_err):
	self.expected_err=expected_err

    def stdout_should_be(self, expected_out):
	self.expected_out=expected_out

    def setUp(self):
	self.stderr=StringIO()
	self.stdout=StringIO()
	self.expected_err=""
	self.expected_out=""
	self.expected_exit_code=0

    def tearDown(self):
	self.check_expectations()	

    def check_expectations(self):
	assert_equals(self.expected_out, self.actual_stdout())
	assert_equals(self.expected_err, self.actual_stderr())
	assert_equals(self.expected_exit_code, self.actual_exit_code)

    def actual_stderr(self):
	return self.stderr.getvalue()

    def actual_stdout(self):
	return self.stdout.getvalue()

