from trashcli.lib.my_input import Input


class User:
    def __init__(self,
                 prepare_output_message,
                 input, # type: Input
                 parse_reply):
        self.prepare_output_message = prepare_output_message
        self.input = input
        self.parse_reply = parse_reply

    def confirm(self, items_to_confirm):
        reply = self.input.read_input(self.prepare_output_message(items_to_confirm))
        return self.parse_reply(reply)
