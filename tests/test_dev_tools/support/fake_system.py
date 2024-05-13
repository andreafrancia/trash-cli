class FakeSystem:
    def __init__(self):
        self.clean = False
        self.os_system_calls = []

    def set_dirty(self):
        self.clean = False

    def set_clean(self):
        self.clean = True

    def os_system(self, cmd):
        self.os_system_calls.append(cmd)
        if cmd == 'git diff-index --quiet HEAD' and self.clean:
            return 0
