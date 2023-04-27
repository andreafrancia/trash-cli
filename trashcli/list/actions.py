from trashcli.super_enum import SuperEnum


class Action(SuperEnum):
    debug_volumes = 'debug_volumes'
    print_version = 'print_version'
    list_trash = 'list_trash'
    list_volumes = 'list_volumes'
    list_trash_dirs = 'list_trash_dirs'
    print_python_executable = 'print_python_executable'
