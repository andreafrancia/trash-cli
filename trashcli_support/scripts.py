from textwrap import dedent

class Scripts:
    def __init__(self, write_file, make_file_executable):
        self.write_file = write_file
        self.make_file_executable = make_file_executable
        self.created_scripts = []

    def add_script(self, name, module, main_function):
        script_contents = dedent("""\
            #!/usr/bin/env python
            from __future__ import absolute_import
            import sys
            from %(module)s import %(main_function)s as main
            sys.exit(main())
            """) % locals()
        self.write_file(name, script_contents)
        self.make_file_executable(name)
        self.created_scripts.append(name)
