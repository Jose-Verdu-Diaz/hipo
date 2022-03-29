'''Auxiliary functions to process image data

This module contains functions for loading, saving, displaying
and processing image data. 

Author: José Verdú Díaz

Methods
-------
parse_tiff
    Parses a hyperion tiff file with multiple images
normalize
    Normalize images with a quantile
show_image
    Displays an image
load_image
    Load an image
create_gif
    Create an animated gif
'''

import napari
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import gridspec
from PIL import Image

from lib.models.Colors import Color


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



def view_histogram(images, channels, geojson_file):
    img_size = Image.fromarray(images[0]).size
    mask = make_mask(geojson_file, img_size) # make_mask() removed

    sns.set_theme(style="darkgrid")
    
    colors = ['#33964a', '#4d3396', '#963338', '#d38123', '#279db5', '#96bc18']

    x = list(range(0,256))

    p = 0.99
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


def show_napari_segmentation(img, labels):
    color = Color()

    viewer = napari.Viewer()

    viewer.add_image(img, name = 'Image')
    viewer.add_labels(labels, name = 'Image')

    print(f'{color.CYAN}Opening napari. Close napari window to continue...{color.ENDC}')
    napari.run()