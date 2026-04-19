from __future__ import absolute_import


def sanitize_for_output(s):
    # Map C0 controls (except TAB) and DEL to caret notation to neutralize
    # terminal escape sequences from attacker-controlled filenames.
    if s is None:
        return s
    return ''.join(
        '^?' if ord(c) == 0x7F
        else '^' + chr(ord(c) ^ 0x40) if ord(c) < 0x20 and ord(c) != 0x09
        else c for c in s)
