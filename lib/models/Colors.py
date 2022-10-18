"""Color codes for the terminal

This module contains the class Color, used to
obtain different terminal color codes

Author: José Verdú Díaz
"""


class Color:
    def __init__(self):
        self.RED = "\033[31m"
        self.GREEN = "\033[32m"
        self.YELLOW = "\033[33m"
        self.BLUE = "\033[34m"
        self.PURPLE = "\033[35m"
        self.CYAN = "\033[36m"
        self.GREY = "\033[90m"

        self.ENDC = "\033[m"
        self.BOLD = "\033[01m"
        self.UNDERLINE = "\033[04m"
        self.REVERSE = "\033[07m"
        self.STRIKETHROUGH = "\033[09m"
