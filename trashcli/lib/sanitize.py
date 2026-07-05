from __future__ import absolute_import

# Control codes with a short mnemonic, as used by GNU ls/rm.
_MNEMONICS = {
    0x07: 'a', 0x08: 'b', 0x09: 't', 0x0a: 'n',
    0x0b: 'v', 0x0c: 'f', 0x0d: 'r',
}

# Characters that never need quoting.
_SAFE = set(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "%+-./:=@_,")


def _is_printable(cp):
    return not (cp < 0x20 or cp == 0x7f or 0x80 <= cp <= 0x9f)


def shell_escape(s):
    """Quote a name the way GNU ls and rm do (shell-escape style)."""
    if s is None or (s != '' and all(c in _SAFE for c in s)):
        return s
    out = []
    in_quotes = False
    for c in s:
        cp = ord(c)
        if not _is_printable(cp):
            if in_quotes:
                out.append("'")
                in_quotes = False
            out.append("$'\\%s'" % _MNEMONICS[cp] if cp in _MNEMONICS
                       else "$'\\%03o'" % cp)
            continue
        if not in_quotes:
            out.append("'")
            in_quotes = True
        out.append("'\\''" if c == "'" else c)
    if in_quotes:
        out.append("'")
    return ''.join(out)


def quoting_wanted(stream, env):
    # Like ls: quote for a terminal, print names raw when piped or redirected.
    if env.get('TRASH_RAW_OUTPUT'):
        return False
    try:
        return bool(stream.isatty())
    except Exception:
        return False
