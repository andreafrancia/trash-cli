def reformat_help_message(help_message):  # type: (str) -> str
    return _collapse_usage_paragraph(_normalize_options(help_message))


def _normalize_options(help_message):  # type: (str) -> str
    return help_message.replace('optional arguments', 'options')


def _collapse_usage_paragraph(help_message):  # type: (str) -> str
    paragraphs = split_paragraphs(help_message)
    return '\n'.join(
        [normalize_spaces(paragraphs[0]) + "\n"]
        + paragraphs[1:])


def normalize_spaces(text):  # type: (str) -> str
    return " ".join(text.split())


def split_paragraphs(text):
    paragraphs = []
    par = ''
    for line in text.splitlines(True):
        if _is_empty_line(line):
            paragraphs.append(par)
            par = ''
        else:
            par += line

    paragraphs.append(par)
    return paragraphs


def _is_empty_line(line):
    return '' == line.strip()
