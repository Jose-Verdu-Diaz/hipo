'''Auxiliary interface functions

This module contains functions to provide the user with an interface to load and save data.

Author: José Verdú Díaz

Methods
-------
'''

import os
import sys
import tkinter as tk
from tkinter.filedialog import askopenfilename
import pandas as pd
from tabulate import tabulate

from lib.utils import clear

def load_input(sample):
    files = os.listdir(f'samples/{sample}/input')

    if not len(files) == 3:
        print(f'3 files expected, found {len(files)}.')
        sys.exit()

    geojson_file, txt_file, tiff_file = '','',''

    for f in files:
        if f.endswith('.txt') and txt_file == '': txt_file = f'samples/{sample}/input/{f}'
        elif f.endswith('.tiff') and tiff_file == '': tiff_file = f'samples/{sample}/input/{f}'
        elif f.endswith('.geojson') and geojson_file == '': geojson_file = f'samples/{sample}/input/{f}'
        else:
            print('Enexpected error, check input files.')
            sys.exit()

    return tiff_file, txt_file, geojson_file


