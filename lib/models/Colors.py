"""Color codes for the terminal

This module contains the class Color, used to
obtain different terminal color codes

Author: José Verdú-Díaz
"""


class Color:
    def __init__(self) -> None:
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


class Colormap:
    def __init__(self) -> None:
        self.i = 0
        self.colors = [
            [54 / 255, 201 / 255, 179 / 255, 1],
            [209 / 255, 14 / 255, 37 / 255, 1],
            [165 / 255, 191 / 255, 51 / 255, 1],
            [211 / 255, 81 / 255, 6 / 255, 1],
            [209 / 255, 54 / 255, 193 / 255, 1],
            [203 / 255, 206 / 255, 47 / 255, 1],
            [2 / 255, 255 / 255, 78 / 255, 1],
        ]

    def next_cmap(self) -> dict:
        cmap = {
            "colors": [[0, 0, 0, 1], self.colors[self.i]],
            "name": f"Cmap {self.i}",
            "interpolation": "linear",
        }
        self.i = self.i + 1 if self.i < len(self.colors) - 1 else 0
        return cmap
