from enum import Enum


class Mode(Enum):
    mode_unspecified = 'mode_unspecified'
    mode_interactive = 'mode_interactive'
    mode_force = 'mode_force'

    def can_ignore_not_existent_path(self):  # type: () -> bool
        return self == Mode.mode_force

    def should_we_ask_to_the_user(self, is_path_accessible):  # type: (bool) -> bool
        return self == Mode.mode_interactive and is_path_accessible
