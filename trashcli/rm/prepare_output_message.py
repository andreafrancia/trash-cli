def prepare_output_message(info_files):
    if not info_files:
        return 'No files to be removed.'
    else:
        return 'The following files will be removed:\n' + '\n'.join(
            '    - ' + info_file for info_file in info_files) + '\nProceed? (y/N) '
