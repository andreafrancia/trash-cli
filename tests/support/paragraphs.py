def normalize_spaces(text):
    return " ".join(text.split())


def split_paragraphs(text):
    paragraphs = []
    par = ''
    for line in text.splitlines(keepends=True):
        if is_empty_line(line):
            paragraphs.append(par)
            par = ''
        else:
            par += line

    paragraphs.append(par)
    return paragraphs


def is_empty_line(line):
    return '' == line.strip()
