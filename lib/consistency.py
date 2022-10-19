"""Consistency functions

This module contains some functions to perform consitency checks
and avoid bugs.

Author: José Verdú-Díaz

Methods
-------
"""

import os


class UnexpectedInputFileAmountException(Exception):
    def __init__(self, file, count, expected):
        message = f"{expected} {file} expected, found {count}!"
        super(UnexpectedInputFileAmountException, self).__init__(message)


class UnknownInputFileException(Exception):
    def __init__(self, files):
        message = f"Unknown input files: {files}!"
        super(UnknownInputFileException, self).__init__(message)


def check_input_files(sample):
    """Checks if the input directory has the necessary files

    Parameters
    ----------
    sample
        Sample to be checked

    Returns
    -------
    UnexpectedInputFileAmountException
        If the amount of a file is not the expected
    UnknownInputFileException
        If there is any unknown file
    None
        If everything is ok
    """

    files = os.listdir(f"samples/{sample}/input")

    geojson_file, txt_file, tiff_file, unknown_file = [], [], [], []

    for f in files:
        path = f"samples/{sample}/input/{f}"
        if f.endswith(".txt"):
            txt_file.append(path)
        elif f.endswith(".tiff"):
            tiff_file.append(path)
        elif f.endswith(".geojson"):
            geojson_file.append(path)
        else:
            unknown_file.append(path)

    file_dict = {"geojson": geojson_file, "txt": txt_file, "tiff": tiff_file}
    for f in file_dict:
        if not len(file_dict[f]) == 1:
            return UnexpectedInputFileAmountException(f, len(file_dict[f]), 1)

    if not len(unknown_file) == 0:
        return UnknownInputFileException(unknown_file)

    return None
