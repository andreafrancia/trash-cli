# Copyright (C) 2011-2024 Andrea Francia Trivolzio(PV) Italy

from tests.support.asserts import assert_equals_with_unidiff
from tests.test_list.cmd.support.trash_list_user import trash_list_user

user = trash_list_user


class TestVersion:
    def test_should_output_the_version(self, user):
        user.set_version('1.2.3')

        output = user.run_trash_list('--version')

        assert_equals_with_unidiff('trash-list 1.2.3\n',
                                   output.whole_output())
