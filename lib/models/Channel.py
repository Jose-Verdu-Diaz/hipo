import cv2
import numpy as np
from scipy import ndimage
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from skimage.morphology import reconstruction

from lib.models.Colors import Color


class Channel:

    def __init__(self, name=None, label=None, image=None, th=None, contrast_limits=None):
        self.name = name
        self.label = label
        self.th = th
        self.contrast_limits = contrast_limits

        self.image = image
        self.image_norm = None
        self.image_cont = None
        self.image_thre = None

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
        self.image_thre = None
        return self 

####################################################################
######################### IMAGE PROCESSING #########################
####################################################################

    def apply_mask(self, mask, img = None):
        if isinstance(img, np.ndarray): return np.where(mask, img, 0)
        else: return np.where(mask, self.image, 0)


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


    def threshold(self):
        clr = Color()
        print(f'{clr.GREY}Applying threshold on channel {self.name}{clr.ENDC}')
        self.image_thre = np.where(self.image_cont >= self.th, self.image_cont, 0)
        return self

####################################################################
############################ ANALYSIS ##############################
####################################################################

    def analyse(self, mask):
        mask_positive = np.logical_and(mask, self.image_thre > 0)
        positive_pixels = self.image_thre[mask_positive]
        all_pixels = self.image_thre[mask]
        mean_positive = np.mean(positive_pixels)
        area_positive = np.sum(mask_positive)
        mean_all = np.mean(all_pixels)
        area_all = np.sum(mask)
        positive_fraction = float(area_positive)/float(area_all)
        summary_dict = {
            "Channel": self.name,    
            "Positive Area" : area_positive,
            "Positive Mean" : mean_positive,
            "Total Area": area_all,
            "Total Mean" : mean_all, 
            "Positive Fraction" : positive_fraction
        }
        return summary_dict


    def segment_fibers(self, mask):

        img = np.array(self.image_thre * 255, dtype='uint8')

        inverted = np.invert(img)
        seed = np.copy(inverted)
        seed = np.where(inverted > 0, inverted.max(), 0)
        filled = reconstruction(seed, inverted, method='erosion')
        filled = np.invert(np.array(filled, dtype='uint8'))

        thresh = cv2.threshold(filled, 0, 255, cv2.THRESH_BINARY_INV)[1]
        thresh = self.apply_mask(mask, img=thresh)

        kernel = np.ones((4, 4), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 1)

        kernel = np.array([
            [0,1,1,0],
            [1,1,1,1],
            [1,1,1,1],
            [0,1,1,0]
        ], np.uint8)
        erode = cv2.erode(opening, kernel, iterations=2)

        D = ndimage.distance_transform_edt(erode)
        localMax = peak_local_max(D, indices=False, min_distance=20, labels=erode)
        
        markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
        labels = watershed(-D, markers, mask=thresh)

        return labels