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

from lib.models.Colors import Color

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
    df = pd.DataFrame(list(zip(dirs)), columns=['Sample'])
    table = tabulate(df, headers = 'keys', tablefmt = 'github')
    return table, df


def sample_df(images, metals, labels, summary_df, sample_name):
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
    with open(f'samples/{sample_name}/{sample_name}.json', 'r') as f: data = json.load(f)
    channel_threshold = ['-' if c['threshold'] == None else c['threshold'] for c in data['channels']]
    channel_contrast = ['-' if c['contrast_limits'] == None else c['contrast_limits'] for c in data['channels']]

    df = pd.DataFrame(
            list(zip(images, metals, labels, img_sizes, pixel_min, pixel_max)),
            columns =['Image', 'Channel', 'Label', 'Image Size', 'Min', 'Max']
        )

    df = df.sort_values(['Channel']).reset_index(drop=True)

    df['Th.'] = channel_threshold # channel_threshold is already sorted, add it after sorting DataFrame
    df['Cont.'] = channel_contrast # channel_contrast is already sorted, add it after sorting DataFrame

    table = tabulate(df.loc[:, df.columns != 'Image'], headers = 'keys', tablefmt = 'github')
    table = f'{color.BOLD}{color.UNDERLINE}Displaying sample:{color.ENDC} {sample_name}\n\n{table}'

    return table, df
