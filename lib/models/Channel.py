import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw


class Channel:

    def __init__(self, name=None, label=None, image=None, threshold=None, contrast_limits=None):
        self.name = name
        self.label = label
        self.image = image
        self.threshold = threshold
        self.contrast_limits = contrast_limits

        self.image_norm = None
        self.image_cont = None

####################################################################
######################### IMAGE PROCESSING #########################
####################################################################

    def apply_mask(self, mask):
        return np.where(mask, self.image, 0)


    def normalize(self, mask):
        masked = self.apply_mask(mask)
        max_val = masked.max()
        img_normalized = np.minimum(masked / max_val, 1.0)
        self.image_norm = np.array(np.round(255.0 * img_normalized), dtype = np.uint8)
        return self

    def contrast(self):
        print(f'Applying contrast on channgel: {self.name}')
        quant_lower = np.quantile(self.image_norm, self.contrast_limits[0] / 100)
        quant_upper = np.quantile(self.image_norm, self.contrast_limits[1] / 100)
        update_contrast = lambda x, a, b: (x - a) / (b - a)
        self.image_cont = update_contrast(self.image_norm, quant_lower, quant_upper)
        self.image_cont = np.where(self.image_cont > 0, self.image_cont, 0)
        self.image_cont = np.where(self.image_cont < 1, self.image_cont, 1)
        return self

