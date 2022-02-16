'''Auxiliary interface functions

This module contains functions to provide the user with an interface to load and save data.

Author: José Verdú Díaz

Methods
-------
ask_file(str, str, list(tuple)) -> str
    Open a dialog to select a file
'''

import os
import sys
import tkinter as tk
from tkinter.filedialog import askopenfilename
import pandas as pd
from tabulate import tabulate

def load_input():
    files = os.listdir('../input')

    if not len(files) == 3:
        print(f'3 files expected, found {len(files)}.')
        sys.exit()

    geojson_file, txt_file, tiff_file = '','',''

    for f in files:
        if f.endswith('.txt') and txt_file == '': txt_file = f'../input/{f}'
        elif f.endswith('.tiff') and tiff_file == '': tiff_file = f'../input/{f}'
        elif f.endswith('.geojson') and geojson_file == '': geojson_file = f'../input/{f}'
        else:
            print('Enexpected error, check input files.')
            sys.exit()

    return tiff_file, txt_file, geojson_file

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def display_img_df(images,metals,labels, summary_df):

    img_sizes = [img.shape for img in images]
    pixel_min = summary_df['MinValue'].tolist()
    pixel_max = summary_df['MaxValue'].tolist()

    df = pd.DataFrame(list(zip(metals, labels, img_sizes, pixel_min, pixel_max)),columns =['Channel', 'Label', 'Image Size', 'Min Value', 'Max Value'])

    clear()
    print(tabulate(df, headers = 'keys', tablefmt = 'psql'))


