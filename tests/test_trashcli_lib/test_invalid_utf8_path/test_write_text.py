import six

from trashcli.lib.printable import write_text


class FakePy2Stream:
    def __init__(self, encoding):
        self.encoding = encoding
        self.written = b''

    def write(self, data):
        assert isinstance(data, bytes)
        self.written += data


class FakeTextStream:
    def __init__(self, encoding=None):
        self.encoding = encoding
        self.written = u''

    def write(self, data):
        if self.encoding:
            data.encode(self.encoding)
        self.written += data


def test_on_python2_an_ascii_stream_gets_escaped_bytes(monkeypatch):
    monkeypatch.setattr(six, 'PY2', True)
    stream = FakePy2Stream('ascii')

    write_text(stream, u'caf\xe9')

    assert stream.written == b'caf\\xe9\n'


def test_on_python2_a_utf8_stream_gets_utf8_bytes(monkeypatch):
    monkeypatch.setattr(six, 'PY2', True)
    stream = FakePy2Stream('utf-8')

    write_text(stream, u'caf\xe9')

    assert stream.written == u'caf\xe9\n'.encode('utf-8')


def test_on_python3_the_stream_gets_text(monkeypatch):
    monkeypatch.setattr(six, 'PY2', False)
    stream = FakeTextStream()

    write_text(stream, u'caf\xe9')

    assert stream.written == u'caf\xe9\n'


def test_on_python3_an_ascii_stream_gets_escaped_text(monkeypatch):
    monkeypatch.setattr(six, 'PY2', False)
    stream = FakeTextStream('ascii')

    write_text(stream, u'caf\xe9')

    assert stream.written == u'caf\\xe9\n'


def test_on_python3_a_utf8_stream_keeps_text(monkeypatch):
    monkeypatch.setattr(six, 'PY2', False)
    stream = FakeTextStream('utf-8')

    write_text(stream, u'caf\xe9')

    assert stream.written == u'caf\xe9\n'
