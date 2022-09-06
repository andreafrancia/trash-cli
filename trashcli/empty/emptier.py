class Emptier:
    def __init__(self, main_loop, delete_mode):
        self.main_loop = main_loop
        self.delete_mode = delete_mode

    def do_empty(self, trash_dirs):
        self.main_loop.do_loop(trash_dirs, self.delete_mode)
