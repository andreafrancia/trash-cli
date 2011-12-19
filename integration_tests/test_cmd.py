# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy

from cmd import Command
from unittest import TestCase
from nose.tools import raises, assert_equals, assert_true, assert_not_equals

class CommandTest(TestCase):
    def test_run_returns_exit_code(self):
        result=Command("false").run()
        assert_not_equals(0, result.exit_code)

        result=Command("true").run()
        assert_equals(0, result.exit_code)

    def test_run_returns_output(self):
        result=Command(["/bin/echo", "foo"]).run()
        assert_equals("foo\n", result.stdout)

        result=Command(["/bin/echo", "-n", "foo"]).run()
        assert_equals("foo", result.stdout)

    def test_run_returns_error_messages(self):
        result=Command(["python", "--bad-option"]).run()
        assert_true(result.stderr.startswith("Unknown option: --"),
                    "This may fail even if the code works")

    def test_run_reads_the_input(self):
        result=Command("cat").run("text")
        assert_equals("text", result.stdout)

    def test_run_honors_env(self):
        result=Command("/usr/bin/env",{'VAR':'value'}).run()
        assert_equals('VAR=value\n', result.stdout)

    def test_env_empty_by_default(self):
        result=Command("/usr/bin/env").run()
        assert_equals('', result.stdout)

    @raises(TypeError)
    def test_mistake_is_detected(self):
        Command("/bin/ls", "-l") # <-- mistake, correct --> Command(["ls","-l"])
