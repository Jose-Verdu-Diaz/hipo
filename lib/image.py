'''Auxiliary functions to process image data

This module contains functions for loading, saving, displaying
and processing image data. 

Author: José Verdú Díaz

Methods
-------
parse_tiff(str, str) -> array,array,array
    Reads and parses a multi-image tiff
'''

import os
import numpy as np
from PIL import Image
import tifffile as tf
import pandas as pd
import seaborn as sns
import seaborn_image as isns

def parse_tiff(tiff_path, summary_path):
    '''Reads and parses a multi-image tiff

    Parameters
    ----------
    tiff_path : str
        Path to tiff multi-image
    summary_path : str
        Path to tiff summary

    Returns
    -------
    tiff_slices : array of shape (n,w,h)
        Array of n tiff images with width w and height h
    metals : 
    labels : 
    '''

    tiff_slices = tf.TiffFile(tiff_path).asarray()
    metals, labels = [], []

    summary_df = pd.read_csv(summary_path, sep = '\t')

    for slice in range(tiff_slices.shape[0]):
        metals.append(str(summary_df['Channel'][slice]))
        labels.append(str(summary_df['Label'][slice]))

    return tiff_slices,metals,labels,summary_df

def normalize_quantile(top_quantile, img, metal):
    max_val = np.quantile(img, top_quantile)

    if max_val == 0: 
        max_val = img.max()
        print(f'Channel {metal} has a {top_quantile} quantile of 0. Using max value: {max_val}')     

    img_normalized = np.minimum(img / max_val, 1.0)
    img_normalized = Image.fromarray(np.array(np.round(255.0 * img_normalized), dtype = np.uint8))
    img_normalized.save(os.path.join('../output', metal + '.jpg'), quality = 100)

def show_image(img):
    isns.imgplot(img)