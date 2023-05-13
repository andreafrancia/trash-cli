from trashcli.restore.output import Output
from trashcli.restore.output_event import Println, Die, Quit, Exiting


class RealOutput(Output):
    def __init__(self, stdout, stderr, exit):
        self.stdout = stdout
        self.stderr = stderr
        self.exit = exit

    def quit(self):
        self.die('')

    def printerr(self, msg):
        print("%s" % msg, file=self.stderr)

    def println(self, line):
        print("%s" % line, file=self.stdout)

    def die(self, error):
        self.printerr(error)
        self.exit(1)

    def append_event(self,
                     event,  # type: OutputEvent
                     ):
        if isinstance(event, Println):
            self.println(event.msg)
        elif isinstance(event, Die):
            self.die(event.msg)
        elif isinstance(event, Quit):
            self.quit()
        elif isinstance(event, Exiting):
            self.println("Exiting")
        else:
            raise Exception("Unknown call %s" % event)
