import numpy as np
import pandas as pd


class Channel:

    def __init__(self, name:str=None, label:str=None, th=None, points=pd.DataFrame(), image=None):
        self.name = name
        self.label = label
        self.th = th
        self.points = points

        self.image = image

####################################################################
################### LOADING AND SAVING FUNCTIONS ###################
####################################################################

    #def save(self, sample):
    #    np.savez_compressed(f'samples/{sample}/{self.name}.npz', self.image_norm)

    
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
        return self 

####################################################################
######################### IMAGE PROCESSING #########################
####################################################################

    def apply_mask(self, mask, img = None):
        if isinstance(img, np.ndarray): return np.where(mask, img, 0)
        else: return np.where(mask, self.image, 0)

####################################################################
############################ ANALYSIS ##############################
####################################################################

    def analyse(self, mask):
        mask_positive = np.logical_and(mask, self.image >= self.th)
        positive_pixels = self.image[mask_positive]
        all_pixels = self.image[mask]
        mean_positive = np.mean(positive_pixels)
        area_positive = np.sum(mask_positive)
        mean_all = np.mean(all_pixels)
        area_all = np.sum(mask)
        positive_fraction = float(area_positive)/float(area_all)
        summary_dict = {
            'Channel': self.name,
            'Threshold': self.th,  
            'Positive Area' : area_positive,
            'Positive Mean' : mean_positive,
            'Total Area': area_all,
            'Total Mean': mean_all, 
           ' Positive Fraction': positive_fraction
        }
        return summary_dict
