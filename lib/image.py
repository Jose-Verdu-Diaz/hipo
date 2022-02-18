'''Auxiliary functions to process image data

This module contains functions for loading, saving, displaying
and processing image data. 

Author: José Verdú Díaz

Methods
-------
'''

import os
import numpy as np
from PIL import Image, ImageDraw
import tifffile as tf
import pandas as pd
import seaborn as sns
import seaborn_image as isns
import matplotlib.pyplot as plt

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

        label =str(summary_df['Label'][slice])
        labels.append(label if not label == 'nan' else '-')

    return tiff_slices,metals,labels,summary_df

def normalize_quantile(top_quantile, img, sample, channel):
    max_val = np.quantile(img, top_quantile)

    if max_val == 0: 
        max_val = img.max()
        print(f'Channel {channel} has a {top_quantile} quantile of 0. Using max value: {max_val}')     

    img_normalized = np.minimum(img / max_val, 1.0)
    img_normalized = Image.fromarray(np.array(np.round(255.0 * img_normalized), dtype = np.uint8))
    img_normalized.save(os.path.join(f'samples/{sample}/img_norm', channel + '.png'), quality = 100)

def show_image(img):  
    isns.imgplot(np.flipud(img))
    plt.show()

def save_image(img, channel, sample):
    img_normalized = Image.fromarray(np.array(img, dtype = np.uint32))
    img_normalized.save(os.path.join(f'samples/{sample}/img_raw', channel + '.png'), quality = 100)

def load_image(path):
    img = Image.open(path)
    return np.asarray(img)

def create_gif(images, sample, channels = None):

    out = []

    for img in images:

        converted = Image.fromarray(img).convert('P')
        #draw = ImageDraw.Draw(converted)
        #draw.text((50, 50), "Sample Text", 150)

        out.append(converted)
        

    out[0].save(f'samples/{sample}/image_animation.gif', save_all=True, append_images=out[1:], optimize=False, duration=1000, loop=0)
