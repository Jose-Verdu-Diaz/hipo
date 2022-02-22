'''Auxiliary functions to process image data

This module contains functions for loading, saving, displaying
and processing image data. 

Author: José Verdú Díaz

Methods
-------
parse_tiff
    Parses a hyperion tiff file with multiple images
normalize_quantile
    Normalize images with a quantile
show_image
    Displays an image
load_image
    Load an image
create_gif
    Create an animated gif
'''

import os
import json
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw
import tifffile as tf
import pandas as pd
import seaborn as sns
import seaborn_image as isns
import matplotlib.pyplot as plt

from lib.Colors import Color
from lib.interface import update_sample_json

def parse_tiff(tiff_path, summary_path):
    '''Parses a hyperion tiff file with multiple images

    Parameters
    ----------
    tiff_path
        Path of tiff file
    summary_path
        Path to summary file

    Returns
    -------
    tiff_slices
        Numpy array of images
    metals
        List of metals
    labels
        List of labels
    summary_df
        Pandas DataFrame with the data of the summary file
    '''

    tiff_slices = tf.TiffFile(tiff_path).asarray()
    metals, labels = [], []

    summary_df = pd.read_csv(summary_path, sep = '\t')

    for slice in range(tiff_slices.shape[0]):
        metals.append(str(summary_df['Channel'][slice]))

        label =str(summary_df['Label'][slice])
        labels.append(label if not label == 'nan' else '-')

    return tiff_slices, metals, labels, summary_df


def normalize_quantile(top_quantile, images, sample, metals):
    '''Normalize images with a quantile

    Normalizing by a quantile instead of normalizing by the max
    value helps avoiding the effect of high-valued artifacts.
    However, it causes clipping in the higher values. Tune the
    parameter top_quantile carefully.

    Parameters
    ----------
    top_quantile
        Top quantile to select max value. Set to 1 to use the max
        pixel value of the image.
    images
        Numpy array of images
    sample
        Name of the sample
    metals
        List of metals
    '''

    update_sample_json(sample, {'norm_quant': top_quantile})

    color = Color()
    warnings = []

    for i,img in enumerate(tqdm(images, postfix=False)):

        max_val = np.quantile(img, top_quantile)

        if max_val == 0: 
            max_val = img.max()
            warnings.append(f'Channel {metals[i]} has a {top_quantile} quantile of 0. Using max value: {max_val}')     

        img_normalized = np.minimum(img / max_val, 1.0)
        img_normalized = Image.fromarray(np.array(np.round(255.0 * img_normalized), dtype = np.uint8))
        img_normalized.save(os.path.join(f'samples/{sample}/img_norm', metals[i] + '.png'), quality = 100)
    
    for w in warnings: print(f'{color.YELLOW}{w}{color.ENDC}')


def show_image(img):
    '''Displays an image

    Parameters
    ----------
    img
        image to be displayed
    '''

    isns.imgplot(np.flipud(img))
    plt.show()


def load_image(path):
    '''Load an image

    Parameters
    ----------
    path
        Path to image file

    Returns
    -------
        Numpy array representing the image
    '''

    img = Image.open(path)
    return np.asarray(img)


def create_gif(images, sample, channels = None):
    '''Create an animated gif

    Parameters
    ----------
    images
        Numpy array of images
    sample
        Name of the sample
    channels, optional
        List of channel names, by default None
    '''

    out = []

    for img in images:
        converted = Image.fromarray(img).convert('P')
        #draw = ImageDraw.Draw(converted)
        #draw.text((50, 50), "Sample Text", 150)

        out.append(converted)      

    out[0].save(f'samples/{sample}/image_animation.gif', save_all=True, append_images=out[1:], optimize=False, duration=1000, loop=0)


def make_mask(geojson_file, size):
    '''Creates mask images from coordinates tuples list

    Parameters
    ----------
    geojson_file
        path to geojson
    size
        Size of the mask

    Returns
    -------
        Numpy array representing the mask
    '''

    with open(geojson_file) as f: annotation_data = json.load(f)

    black = Image.new('1', size)
    imd = ImageDraw.Draw(black)

    for ann in annotation_data["features"]:

        blob = ann["geometry"] # We assume there is only 1 ROI, this should be fixed 

        if blob["type"] == "LineString": coords = blob["coordinates"]
        if blob["type"] == "Polygon": coords = blob["coordinates"][0]

        tuples = [tuple(coord) for coord in coords]
        imd.polygon(tuples,fill="white",outline="white")

    return np.array(black)


def apply_ROI(geojson_file, images):
    '''Masks ROIs from images

    Parameters
    ----------
    geojson_file
        Path to geojson file
    images
        Images to mask

    Returns
    -------
    masked
        masked images
    '''

    img_size = Image.fromarray(images[0]).size # We assume all images of a sample have the same size
    mask = make_mask(geojson_file, img_size)

    masked = []
    for img in images: masked.append(np.where(mask, img, 0))

    return masked

def appy_threshold(sample, images, channels, threshold):
    '''Applies threshold to images and saves them

    Parameters
    ----------
    sample
        Sample name
    images
        List of np arrays representing the images
    channels
        List of channel names of the images
    threshold
        Threshold to be applied
    '''

    for i, img in enumerate(images):
        img = img / 255
        result = np.where(img > threshold, img, 0)
        result = Image.fromarray(np.array(np.round(255.0 * result), dtype = np.uint8))
        result.save(os.path.join(f'samples/{sample}/img_threshold', channels[i] + '.png'), quality = 100)
        


