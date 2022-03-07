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

import lib.browse as browse

# Key: name of the dir where the operation output will appear
# Value: list of sample json parameters, corresponding to the required operations
OPERATION_REQUIREMENTS = {
    'img_norm': [],
    'img_cont': ['norm'],
    'analysis': ['img_roi']
}

# Key: json parameter, corresponding to the required operations
# Value: name to be displayed
REQUIREMENTS_NAME_MAPPING = {
    'norm': 'ROI and Normalization',
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

class ThresholdExpectedException(Exception):
    def __init__(self, channel):
        message = f'No threshold for the channel {channel}!'
        super(ThresholdExpectedException, self).__init__(message)


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

    table, df = browse.list_samples()
    
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


def check_operation_requirements(sample, operation):
    '''Checks if required operations for a new operation are already done

    Parameters
    ----------
    sample
        Sample to check
    operation
        New operation

    Returns
    -------
    Name of required operation
        if requirements are not met
    None
        If requirements are met
    '''

    with open(f'samples/{sample}/{sample}.json', 'r') as f: data = json.load(f)

    for op_req in OPERATION_REQUIREMENTS[operation]:
        if data[op_req] == None or data[op_req] == False: return REQUIREMENTS_NAME_MAPPING[op_req]
    return None


def check_existing_threshold(**kwargs):
    sample = kwargs['sample']
    channel_id = kwargs['channel_id']

    with open(f'samples/{sample}/{sample}.json', 'r') as f: data = json.load(f)

    if data['channels'][channel_id]['threshold'] == None:
        return ThresholdExpectedException(data['channels'][channel_id]['name'])
    
    return None