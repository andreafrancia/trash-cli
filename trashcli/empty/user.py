class User:
    def __init__(self, prepare_output_message, input, parse_reply):
        self.prepare_output_message = prepare_output_message
        self.input = input
        self.parse_reply = parse_reply

    def do_you_wanna_empty_trash_dirs(self, trash_dirs):
        reply = self.input(self.prepare_output_message(trash_dirs))
        return self.parse_reply(reply)
