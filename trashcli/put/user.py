from trashcli.put.describe import describe


class User:
    def __init__(self, my_input_func):
        self.my_input = my_input_func

    def ask_user_about_deleting_file(self, program_name, path):
        reply = self.my_input("%s: trash %s '%s'? " % (program_name,
                                                       describe(path),
                                                       path))
        return parse_user_reply(reply)


user_replied_no = "user_replied_no"
user_replied_yes = "user_replied_yes"


def parse_user_reply(reply):
    return {False: user_replied_no,
            True: user_replied_yes}[reply.lower().startswith("y")]
