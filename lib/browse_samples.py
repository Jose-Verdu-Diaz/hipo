'''Browse Samples

This module contains functions for browsing the samples

Author: José Verdú Díaz
'''

import os
import pandas as pd
from tabulate import tabulate

from lib.Colors import Color

def list_samples():
    dirs = os.listdir('samples')
    df = pd.DataFrame(list(zip(dirs)), columns=['Sample'])

    return tabulate(df, headers = 'keys', tablefmt = 'github'), df


def display_sample_df(images, metals, labels, summary_df, sample_name):

    color = Color()

    img_sizes = [img.shape for img in images]
    pixel_min = summary_df['MinValue'].tolist()
    pixel_max = summary_df['MaxValue'].tolist()

    df = pd.DataFrame(list(zip(metals, labels, img_sizes, pixel_min, pixel_max)),columns =['Channel', 'Label', 'Image Size', 'Min Value', 'Max Value'])

    table = tabulate(df, headers = 'keys', tablefmt = 'github')
    return f'{color.BOLD}{color.UNDERLINE}Displaying sample:{color.ENDC} {sample_name}\n\n{table}', df