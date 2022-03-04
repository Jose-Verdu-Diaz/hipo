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
from click import style
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw
import tifffile as tf
import pandas as pd
import seaborn as sns
import seaborn_image as isns
import matplotlib.pyplot as plt
from matplotlib import gridspec
import napari

from lib.Colors import Color
from lib.interface import update_sample_json, load_dir_images

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


def normalize_quantile(top_quantile, geojson_file, images, sample, metals):
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

    masked = apply_ROI(geojson_file, images)

    color = Color()
    warnings = []

    for i,img in enumerate(tqdm(masked, desc = 'Normalizing images', postfix=False)):

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
    for img in tqdm(images, desc = 'Applying ROIs', postfix=False): masked.append(np.where(mask, img, 0))
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

    for i, img in enumerate(tqdm(images, desc = 'Thresholding images', postfix=False)):
        img = img / 255
        result = np.where(img > threshold, img, 0)
        result = Image.fromarray(np.array(np.round(255.0 * result), dtype = np.uint8))
        result.save(os.path.join(f'samples/{sample}/img_threshold', channels[i] + '.png'), quality = 100)
        

def analyse_images(sample, geojson_file):
    '''Create a csv report of the thresholded images

    Parameters
    ----------
    sample
        Sample name
    geojson_file
        path to geojson

    Returns
    -------
    None
        if no thresholded images are found
    1
        if ok
    '''

    images, channels = load_dir_images(sample, 'img_threshold')
    if len(images) == 0: return None

    img_size = Image.fromarray(images[0]).size
    mask = make_mask(geojson_file, img_size)

    result = []
    for i, img in enumerate(tqdm(images, desc = 'Analysing images', postfix=False)):
        img = img / 255

        mask_positive = np.logical_and(mask, img > 0)

        positive_pixels = img[mask_positive]
        all_pixels = img[mask]

        mean_positive = np.mean(positive_pixels)
        area_positive = np.sum(mask_positive)

        mean_all = np.mean(all_pixels)
        area_all = np.sum(mask)
        
        positive_fraction = float(area_positive)/float(area_all)

        summary_dict = {
            "Channel": channels[i],    
            "Positive Area" : area_positive,
            "Positive Mean" : mean_positive,
            "Total Area": area_all,
            "Total Mean" : mean_all, 
            "Positive Fraction" : positive_fraction
        }

        result.append(summary_dict)

    result_df = pd.DataFrame(result)
    result_df.to_csv(f'samples/{sample}/analysis.csv',index=False)

    return 1


def show_napari(images, channels):

    color = Color()

    if len(images) > 6:
        input(f'{color.RED}Only 6 images can be displayed at the same time.\nPress enter to continue...{color.ENDC}')
        return

    viewer = napari.Viewer()

    colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']

    for i,img in enumerate(images):
        cmap = create_cmap(colors[i])
        viewer.add_image(img, colormap = cmap, name = channels[i])

    print(f'{color.CYAN}Opening napari. Close napari window to continue...{color.ENDC}')
    napari.run()


def create_cmap(c):

    stop = {
        'red': [1, 0, 0, 1],
        'yellow': [1, 1, 0, 1],
        'green': [0, 1, 0, 1],
        'cyan': [0, 1, 1, 1],
        'blue': [0, 0, 1, 1],
        'magenta': [1, 0, 1, 1]
    }

    colors = np.linspace(
        start = [0, 0, 0, 1],
        stop = stop[c],
        num = 100,
        endpoint = True
    )

    colors[0] = np.array([0, 0, 0, 0])

    new_colormap = {
        'colors': colors,
        'name': c,
        'interpolation': 'linear'
    }

    return new_colormap


def threshold_napari(img, channel):
    color = Color()
    viewer = napari.Viewer()
    viewer.add_image(img, name = channel)
    print(f'{color.CYAN}Opening napari. Close napari window to continue...{color.ENDC}')
    napari.run()

    contrast = viewer.layers[channel].contrast_limits
    input(f'{color.GREEN}The selected contrast limits are: {contrast}. Press Enter to continue...')


def contrast_LUT(img):
    min=np.min(img)
    max=np.max(img)

    LUT=np.zeros(256,dtype=np.uint8)
    LUT[min:max+1]=np.linspace(start=0,stop=255,num=(max-min)+1,endpoint=True,dtype=np.uint8)

    Image.fromarray(LUT[img]).save('result.png')

def view_histogram(images, channels, geojson_file):
    img_size = Image.fromarray(images[0]).size
    mask = make_mask(geojson_file, img_size)

    sns.set_theme(style="darkgrid")
    
    colors = ['#33964a', '#4d3396', '#963338', '#d38123', '#279db5', '#96bc18']

    x = list(range(0,256))

    p = 0.999
    p_lines = ()
    p_labels = ()

    fig = plt.figure(figsize = (25,10))
    fig.suptitle('Histogram of normalized channels (masked)', fontsize=20)
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1], sharex = ax0)
    ax0.set_yscale("log")

    for i, img in enumerate(images):
        img_masked = img[mask]

        counts = img_masked.ravel()
        percentile = np.quantile(img, p)

        y, bins = np.histogram(counts, bins = range(0,257))
        ax0.plot(x, y, label = channels[i], linestyle = '-', color= colors[i])
        ax1.plot(x, y, label = channels[i], linestyle = '-', color= colors[i])
        pline0 = ax0.axvline(percentile, linestyle = 'dotted', color = colors[i])
        p_lines += (pline0,)
        p_labels += (f'{channels[i]} {p * 100}% percentile',)
        ax1.axvline(percentile, linestyle = 'dotted', color = colors[i])

    plt.setp(ax0.get_xticklabels(), visible=False)
    ax0.axvline(0, color='grey', alpha = 0.5)
    ax0.axvline(255, color='grey', alpha = 0.5)
    ax0.legend(p_lines, p_labels, loc='upper right')
    ax0.axhline(1, color='grey', linestyle = 'dotted')
    ax0.set_ylabel('Pixel Counts (log)')
    ax1.axvline(0, color='grey', alpha = 0.5)
    ax1.axvline(255, color='grey', alpha = 0.5)
    ax1.legend(loc='upper right')
    ax1.set_xlabel('Pixel Value')
    ax1.set_ylabel('Pixel Counts')
    ax1.ticklabel_format(style = 'plain')
    plt.xticks(np.append(np.arange(start = 0, stop = 255, step = 10), 255))
    plt.xticks(rotation = 45)
    plt.subplots_adjust(hspace=.02)
    plt.show()