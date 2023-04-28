# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from tests.support.asserts import assert_equals_with_unidiff
from tests.test_list.cmd.setup import Setup


class TestVersion(Setup):
    def test_should_output_the_version(self):
        self.user.set_version('1.2.3')

        self.user.run_trash_list('--version')

        assert_equals_with_unidiff('trash-list 1.2.3\n',
                                   self.user.output())
