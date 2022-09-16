from trashcli.trash import println


class PrintTimeAction:
    def __init__(self, out, clock):
        self.out = out
        self.clock = clock

    def run_action(self, _parsed, environ, _uid):
        now_value = self.clock.get_now_value(environ)
        println(self.out,
                now_value.replace(microsecond=0).isoformat())
