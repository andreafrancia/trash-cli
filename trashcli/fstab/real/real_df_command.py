import subprocess

from trashcli.fstab.protocols.df_command import DfCommand


class RealDfCommand(DfCommand):
    def df_output(self):  # type: () -> str
        process = subprocess.Popen(['df', '-P'],
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, _ = process.communicate()
        return stdout
