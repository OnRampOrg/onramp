
class TerminalFonts(object):

    def __init__(self):
        self.formats = [
            '\033[95m',  # (0) Header
            '\033[94m',  # (1) Okay (Blue)
            '\033[92m',  # (2) Okay (Green)
            '\033[93m',  # (3) Warning (Yellow)
            '\033[91m',  # (4) Fail (Red)
            '\033[1m',   # (5) Bold
            '\033[4m',   # (6) Underline
        ]
        self.ec = '\033[0m'  # End Character

    def format(self, text, index):
        if (index < 0) or (index > len(self.formats) - 1):
            raise ValueError("That is an invalid index! Valid range "
                         "is (0 - {})".format(len(self.formats) - 1))
        else:
            sc = self.formats[index]
            return "{sc}{text}{ec}".format(
                sc=sc, text=text, ec=self.ec)
