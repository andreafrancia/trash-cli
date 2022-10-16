class MyMock:
    def __init__(self, methods=None):
        self.methods = methods or {}

    def __getattr__(self, item):
        def not_implemented():
            raise NotImplementedError

        if item in self.methods:
            return self.methods[item]
        return not_implemented
