class File:
    def __init__(self, content):
        self.content = content

    def getsize(self):
        return len(self.content)
