from six import text_type
from typing import List
from typing import NamedTuple


class Unidiff(NamedTuple('Comparison', [
    ('expected', List[text_type]),
    ('actual', List[text_type]),
])):
    def are_equals(self):
        return self.actual == self.expected

    def unidiff_as_list(self):
        return list(self._as_generator())

    def unidiff_as_single_string(self):
        return ''.join(self._as_generator())

    def _as_generator(self):
        import difflib
        expected = self.expected
        actual = self.actual

        diff = difflib.unified_diff(expected, actual,
                                    fromfile='Expected', tofile='Actual',
                                    lineterm='\n', n=10)

        return diff

