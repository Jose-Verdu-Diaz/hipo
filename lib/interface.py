'''Auxiliary interface functions

This module contains functions to interact with files and directories.

Author: José Verdú Díaz

Methods
-------
load_input
    Load input tiff, summary and annotations
make_sample_dirs
    Creates the directory structure for a new sample
'''

import os
import sys
import json

def load_input(sample):
    '''Load input tiff, summary and annotations

    Parameters
    ----------
    sample
        Sample name to be loaded

    Returns
    -------
    tiff_file
        Path of the tiff image
    txt_file
        Path of the summary file
    geojson_file
        path of the annotations file
    '''

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


def make_sample_dirs(name):
    '''Creates the directory structure for a new sample

    Parameters
    ----------
    name
        Name of the new sample
    '''

    with open('lib/json/sample_dir_structure.json', 'r') as f: data = json.load(f)

    path = f'samples/{name}'
    os.makedirs(path)

    for d in data['sample_name']: os.makedirs(f'{path}/{d}')



