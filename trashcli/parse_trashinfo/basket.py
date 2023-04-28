from __future__ import absolute_import


class Basket:
    def __init__(self, initial_value=None):
        self.collected = initial_value

    def collect(self, value):
        self.collected = value
