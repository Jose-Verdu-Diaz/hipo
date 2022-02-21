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
import shutil
from turtle import update

from lib.Colors import Color
from lib.consistency import check_input_files


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
    
    None
        if there is any exception
    '''

    color = Color()

    while True:

        try:
            result = check_input_files(sample)

            if not result is None: raise result

            files = os.listdir(f'samples/{sample}/input')

            geojson_file, txt_file, tiff_file = '','',''

            for f in files:
                path = f'samples/{sample}/input/{f}'
                if f.endswith('.txt'): txt_file = path
                elif f.endswith('.tiff'): tiff_file = path
                elif f.endswith('.geojson'): geojson_file = path

            return (tiff_file, txt_file, geojson_file)

        except Exception as e: 
            input(f'{color.RED}{e} Press Enter to continue...{color.ENDC}')
            return None


def make_sample_dirs(name):
    '''Creates the directory and file structure for a new sample

    Parameters
    ----------
    name
        Name of the new sample
    '''

    path = f'samples/{name}'
    os.makedirs(path)
    with open('lib/json/sample_dir_structure.json', 'r') as f: data = json.load(f)
    for d in data['sample_name']: os.makedirs(f'{path}/{d}')

    shutil.copy('lib/json/sample_parameters.json',f'{path}/{name}.json')

    update_sample_json(name, {'name': name})


def update_sample_json(name, update_dict = None):
    '''Updates a sample json file

    Parameters
    ----------
    name
        name to sample to update
    update_dict
        Dict of parameters to be updated
    '''

    path = f'samples/{name}/{name}.json'

    with open(path, 'r+') as f: 
        data = json.load(f)

        for param in update_dict: data[param] = update_dict[param]

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def delete_sample(name):
    '''Delete sample directory and all of its contents

    Parameters
    ----------
    name
        Name of the sample to delete
    '''

    color = Color()
    path = f'samples/{name}'
    shutil.rmtree(path)
    input(f'\n{color.GREEN}Sample removed successfully!{color.ENDC}')

