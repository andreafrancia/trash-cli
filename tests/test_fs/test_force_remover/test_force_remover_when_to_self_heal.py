import errno

import pytest

from trashcli.fslib.force_remover import ForceRemover


def eacces():  # type: () -> OSError
    return OSError(errno.EACCES, "Permission denied")


def enoent():  # type: () -> OSError
    return OSError(errno.ENOENT, "No such file or directory")

should_self_heal = ForceRemover.should_self_heal

class TestShouldSelfHeal:
    @pytest.mark.parametrize("error", [eacces()])
    @pytest.mark.parametrize("euid", [1000])
    @pytest.mark.parametrize("in_home_trash", [True])
    def test_self_heals__is_granted_only__on_normal_user__with_home_trash__on_eacces(self, error, euid, in_home_trash):
        assert should_self_heal(error, euid, in_home_trash) is True

    @pytest.mark.parametrize("error", [enoent(), eacces()])
    @pytest.mark.parametrize("euid", [0])
    @pytest.mark.parametrize("in_home_trash", [False, True])
    def test_root__never_needs_self_heal(self, error, euid, in_home_trash):
        assert should_self_heal(error, euid, in_home_trash) is False

    @pytest.mark.parametrize("error", [enoent()])
    @pytest.mark.parametrize("euid", [0])
    @pytest.mark.parametrize("in_home_trash", [False, True])
    def test_does_not_heal_when_the_error_is_not_eacces(self, error, euid, in_home_trash):
        assert should_self_heal(error, euid, in_home_trash) is False

    @pytest.mark.parametrize("error", [enoent(), eacces()])
    @pytest.mark.parametrize("euid", [0, 1000])
    @pytest.mark.parametrize("in_home_trash", [False])
    def test_self_heal__can_be_granted__outside_the_home_trash(self, error, euid, in_home_trash):
        assert should_self_heal(error, euid, in_home_trash) is False

    @pytest.mark.parametrize("error", [enoent()])
    @pytest.mark.parametrize("euid", [0, 1000])
    @pytest.mark.parametrize("in_home_trash", [False, True])
    def test_never_heals_when_the_error_is_not_eacces(self, error, euid, in_home_trash):
        assert should_self_heal(error, euid, in_home_trash) is False
