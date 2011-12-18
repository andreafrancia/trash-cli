# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equals

def test_how_path_joining_works():
    from os.path import join
    assert_equals('/another-absolute', join('/absolute', '/another-absolute'))
    assert_equals('/absolute/relative', join('/absolute', 'relative'))
    assert_equals('/absolute', join('relative', '/absolute'))
    assert_equals('relative/relative', join('relative', 'relative'))
    assert_equals('/absolute', join('', '/absolute'))
    assert_equals('/absolute', join(None, '/absolute'))
