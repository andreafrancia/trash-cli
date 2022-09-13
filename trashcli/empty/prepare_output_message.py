from trashcli.trash_dirs_scanner import trash_dir_found


def prepare_output_message(trash_dirs):
    result = []
    if trash_dirs:
        result.append("Would empty the following trash directories:")
        for event, args in trash_dirs:
            if event == trash_dir_found:
                trash_dir, volume = args
                result.append("    - %s" % trash_dir)
        result.append("Proceed? (y/n) ")
        return "\n".join(result)
    else:
        return 'No trash directories to empty.\n'
