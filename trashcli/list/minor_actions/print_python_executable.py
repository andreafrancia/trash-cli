class PrintPythonExecutable:
    def execute(self, parsed):
        import sys
        print(sys.executable)
