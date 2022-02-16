'''
Author: José Verdú Díaz
'''

import os
import numpy as np
from PIL import Image

from interface import load_input, display_img_df
from image import parse_tiff, normalize_quantile

if __name__ == '__main__':
    
    tiff_file, txt_file, geojson_file = load_input()

    images, metals, labels, summary_df = parse_tiff(tiff_file, txt_file)

    display_img_df(images, metals, labels, summary_df)

    for i, img in enumerate(images): normalize_quantile(0.90, img, metals[i])


