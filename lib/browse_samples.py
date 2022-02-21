'''Browse Samples

This module contains functions for browsing the samples

Author: José Verdú Díaz

Methods
-------
list_samples
    List all the existing samples
display_sample_df
    Generate a table with the information of a sample
'''

import os
import json
import pandas as pd
from tabulate import tabulate

from lib.Colors import Color

def list_samples():
    '''List all the existing samples

    Returns
    -------
    table
        Printable string table of the samples
    df
        Pandas DataFrame with all the samples and some extra
        information
    '''

    dirs = sorted(os.listdir('samples'))

    norm_quant = []

    for d in dirs:
        with open(f'samples/{d}/{d}.json', 'r') as f: data = json.load(f)

        norm_quant.append(data['norm_quant'])

    df = pd.DataFrame(list(zip(dirs, norm_quant)), columns=['Sample', 'Norm. Quant.'])
    table = tabulate(df, headers = 'keys', tablefmt = 'github')
    return table, df


def display_sample_df(images, metals, labels, summary_df, sample_name):
    '''Generate a table with the information of a sample

    Parameters
    ----------
    images
        Numpy array representing the images
    metals
        List of metals
    labels
        List of labels
    summary_df
        Pandas DataFrame with the summary file data
    sample_name
        Name of the sample

    Returns
    -------
    table
        Printable string table with the information of the sample and a header
    df
        Pandas DataFrame containing information of the sample
    '''

    color = Color()

    img_sizes = [img.shape for img in images]
    pixel_min = summary_df['MinValue'].tolist()
    pixel_max = summary_df['MaxValue'].tolist()

    df = pd.DataFrame(list(zip(metals, labels, img_sizes, pixel_min, pixel_max)),columns =['Channel', 'Label', 'Image Size', 'Min Value', 'Max Value'])

    table = tabulate(df, headers = 'keys', tablefmt = 'github')
    table = f'{color.BOLD}{color.UNDERLINE}Displaying sample:{color.ENDC} {sample_name}\n\n{table}'
    return table, df