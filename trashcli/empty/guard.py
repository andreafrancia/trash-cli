class Guard:

    def ask_the_user(self, user, trash_dirs, emptier):
        trash_dirs_list = list(trash_dirs)
        if user.do_you_wanna_empty_trash_dirs(trash_dirs_list):
            emptier.do_empty(trash_dirs_list)
