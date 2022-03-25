import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw

from lib.models.Colors import Color


class Channel:

    def __init__(self, name=None, label=None, image=None, threshold=None, contrast_limits=None):
        self.name = name
        self.label = label
        self.threshold = threshold
        self.contrast_limits = contrast_limits

        self.image = image
        self.image_norm = None
        self.image_cont = None

####################################################################
################### LOADING AND SAVING FUNCTIONS ###################
####################################################################

    def save(self, sample):
        np.savez_compressed(f'samples/{sample}/{self.name}.npz', self.image_norm)

    
    def load_images(self, im_type = 'image', img = None):
        setattr(self, im_type, img)
        return self

    
    def dump_images(self):
        '''Dumps all images of the channel

        Returns
        -------
            Channel
        '''
        self.image = None
        self.image_norm = None
        self.image_cont = None
        return self 

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
        clr = Color()
        print(f'{clr.GREY}Applying contrast on channel {self.name}{clr.ENDC}')
        quant_lower = np.quantile(self.image_norm, self.contrast_limits[0] / 100)
        quant_upper = np.quantile(self.image_norm, self.contrast_limits[1] / 100)
        update_contrast = lambda x, a, b: (x - a) / (b - a)
        self.image_cont = update_contrast(self.image_norm, quant_lower, quant_upper)
        self.image_cont = np.where(self.image_cont > 0, self.image_cont, 0)
        self.image_cont = np.where(self.image_cont < 1, self.image_cont, 1)
        return self

