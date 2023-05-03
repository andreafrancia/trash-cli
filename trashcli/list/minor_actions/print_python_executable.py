class PrintPythonExecutableArgs:
    pass


class PrintPythonExecutable:
    def run_action(self,
                   _args,  # type: PrintPythonExecutableArgs
                   ):
        import sys
        print(sys.executable)
