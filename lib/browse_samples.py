'''Browse Samples

This module contains functions for browsing the samples

Author: José Verdú Díaz
'''

import os
import pandas as pd
from pyparsing import col
from tabulate import tabulate

def list_samples():
    dirs = os.listdir('samples')
    df = pd.DataFrame(list(zip(dirs)), columns=['Sample'])

    print(tabulate(df, headers = 'keys', tablefmt = 'github'))
    return df


def display_sample_df(images, metals, labels, summary_df, sample_name):

    img_sizes = [img.shape for img in images]
    pixel_min = summary_df['MinValue'].tolist()
    pixel_max = summary_df['MaxValue'].tolist()

    df = pd.DataFrame(list(zip(metals, labels, img_sizes, pixel_min, pixel_max)),columns =['Channel', 'Label', 'Image Size', 'Min Value', 'Max Value'])

    print(f'Displayin sample: {sample_name}\n')
    print(tabulate(df, headers = 'keys', tablefmt = 'github'))