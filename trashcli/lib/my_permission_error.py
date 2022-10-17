try:
    MyPermissionError = PermissionError
except NameError:
    MyPermissionError = OSError
MyPermissionError = MyPermissionError
