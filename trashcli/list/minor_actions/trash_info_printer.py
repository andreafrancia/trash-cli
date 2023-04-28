import os

from trashcli.trash import parse_path, ParseError, path_of_backup_copy


def format_line(attribute, original_location):
    return "%s %s" % (attribute, original_location)


def format_line2(attribute, original_location, original_file):
    return "%s %s -> %s" % (attribute, original_location, original_file)


class TrashInfoPrinter:
    def __init__(self, output, file_reader):
        self.output = output
        self.file_reader = file_reader

    def print_trashinfo(self, volume, trashinfo_path, extractor, show_files):
        try:
            contents = self.file_reader.contents_of(trashinfo_path)
        except IOError as e:
            self.output.print_read_error(e)
        else:
            try:
                relative_location = parse_path(contents)
            except ParseError:
                self.output.print_parse_path_error(trashinfo_path)
            else:
                attribute = extractor.extract_attribute(trashinfo_path,
                                                        contents)
                original_location = os.path.join(volume, relative_location)

                if show_files:
                    original_file = path_of_backup_copy(trashinfo_path)
                    line = format_line2(attribute, original_location,
                                        original_file)
                else:
                    line = format_line(attribute, original_location)
                self.output.println(line)
