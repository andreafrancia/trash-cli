from trashcli.lib.action import Action


class PrintPythonExecutableArgs:
    pass


class PrintPythonExecutable(Action):
    def run_action(self,
                   args,  # type: PrintPythonExecutableArgs
                   ):
        import sys
        print(sys.executable)
