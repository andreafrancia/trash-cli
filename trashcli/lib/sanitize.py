from __future__ import absolute_import


def sanitize_for_output(s):
    # Neutralize terminal control sequences in attacker-controlled strings.
    if s is None:
        return s
    out = []
    for c in s:
        cp = ord(c)
        if cp == 0x09:
            out.append(c)
        elif cp < 0x20:
            out.append('^' + chr(cp ^ 0x40))
        elif cp == 0x7F:
            out.append('^?')
        elif 0x80 <= cp <= 0x9F or 0xDC80 <= cp <= 0xDCFF:
            out.append('\\x%02x' % (cp & 0xFF))
        else:
            out.append(c)
    return ''.join(out)
