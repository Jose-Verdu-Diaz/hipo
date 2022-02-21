'''Consistency functions

This module contains some functions to perform consitency checks
and avoid bugs.

Author: José Verdú Díaz

Methods
-------
check_repeated_sample_name
    Check if the sample name already exists
'''

import os
import json

from lib.browse_samples import list_samples

# Key: name of the dir where the operation output will appear
# Value: list of sample json parameters, corresponding to the required operations
OPERATION_REQUIREMENTS = {
    'img_norm': [],
    'img_roi': ['norm_quant']
}
REQUIREMENTS_NAME_MAPPING = {
    'norm_quant': 'Normalization',
    'roi': 'ROI'
}

class RepeatedNameException(Exception):
    def __init__(self, message=f'Repeated name!'):
        super(RepeatedNameException, self).__init__(message)


class UnexpectedInputFileAmountException(Exception):
    def __init__(self, file, count, expected):
        message = f'{expected} {file} expected, found {count}!'
        super(UnexpectedInputFileAmountException, self).__init__(message)

class UnknownInputFileException(Exception):
    def __init__(self, files):
        message = f'Unknown input files: {files}!'
        super(UnknownInputFileException, self).__init__(message)


def check_repeated_sample_name(name):
    '''Check if the sample name already exists

    Parameters
    ----------
    name
        Sample name to be checked

    Returns
    -------
        True if the name doesn't exist
        False if the name already exists
    '''

    table, df = list_samples()
    
    if name in list(df['Sample']):
        return False
    else: return True


def check_input_files(sample):
    '''Checks if the input directory has the necessary files

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
    '''

    files = os.listdir(f'samples/{sample}/input')

    geojson_file, txt_file, tiff_file, unknown_file = [], [], [], []

    for f in files:
        path = f'samples/{sample}/input/{f}'
        if f.endswith('.txt'): txt_file.append(path)
        elif f.endswith('.tiff'): tiff_file.append(path)
        elif f.endswith('.geojson'): geojson_file.append(path)
        else: unknown_file.append(path)

    file_dict = {'geojson': geojson_file, 'txt': txt_file, 'tiff': tiff_file}
    for f in file_dict:
        if not len(file_dict[f]) == 1: return UnexpectedInputFileAmountException(f, len(file_dict[f]), 1)
    
    if not len(unknown_file) == 0: return UnknownInputFileException(unknown_file)

    return None


def check_overwrite(sample, param):
    '''Check if directory files are going to be overwritten

    Parameters
    ----------
    sample
        Name of the sample
    param
        Sample json parameter to check. If the parameter is not None, then overwritting will occur

    Returns
    -------
    True
        if no overwritting
    False
        if overwritting
    '''

    with open(f'samples/{sample}/{sample}.json', 'r') as f: data = json.load(f)

    if data[param] == None: return True
    else: return False

def check_operation_requirements(sample, operation):

    with open(f'samples/{sample}/{sample}.json', 'r') as f: data = json.load(f)

    for op_req in OPERATION_REQUIREMENTS[operation]:
        if data[op_req] == None: return REQUIREMENTS_NAME_MAPPING[op_req]
    return None

