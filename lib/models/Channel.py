import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw


class Channel:

    def __init__(self, name=None, label=None, image=None, threshold=None, contrast=None):
        self.name = name
        self.label = label
        self.image = image
        self.threshold = threshold
        self.contrast = contrast

        self.image_norm = None

####################################################################
######################### IMAGE PROCESSING #########################
####################################################################

    def apply_mask(self, mask):
        return np.where(mask, self.image, 0)


    def normalize(self, mask):
        masked = self.apply_mask(mask)
        max_val = masked.max()
        img_normalized = np.minimum(masked / max_val, 1.0)
        self.image_norm = Image.fromarray(np.array(np.round(255.0 * img_normalized), dtype = np.uint8))
        return self