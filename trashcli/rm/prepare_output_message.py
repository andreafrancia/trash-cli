def prepare_output_message(files_to_remove):
    if not files_to_remove:
        return 'No files to be removed.'
    else:
        return 'The following files / directories will be removed:\n' + '\n'.join(
            '    - ' + file[0] for file in files_to_remove) + '\nProceed? (y/N) '
