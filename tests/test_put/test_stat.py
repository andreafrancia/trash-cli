from tests.run_command import temp_dir
from trashcli.put.fs.real_fs import RealFs


def octal(n):  # type: (int) -> str
    o = oct(n)

    def remove_octal_prefix(o):
        if o.startswith('0o'):
            return o[2:]
        elif o.startswith('0'):
            return o[1:]
        else:
            ValueError('Invalid octal format: %s' % o)

    return "%s%s" % ("0o", remove_octal_prefix(o))


class TestOctal:
    def test(self):
        assert octal(16877) == '0o40755'


class TestStat:
    def test(self, temp_dir):
        fs = RealFs()
        fs.mkdir(temp_dir / 'foo')
        stat = fs.lstat(temp_dir / 'foo')
        assert stat.mode == 16877
