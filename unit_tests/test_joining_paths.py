# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equal

def test_how_path_joining_works():
    from os.path import join
    assert_equal('/another-absolute', join('/absolute', '/another-absolute'))
    assert_equal('/absolute/relative', join('/absolute', 'relative'))
    assert_equal('/absolute', join('relative', '/absolute'))
    assert_equal('relative/relative', join('relative', 'relative'))
    assert_equal('/absolute', join('', '/absolute'))
    assert_equal('/absolute', join(None, '/absolute'))
