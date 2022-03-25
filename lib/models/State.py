import os
import numpy as np
import pandas as pd
import tabulate as tblt

from lib.models.Sample import Sample
from lib.models.Colors import Color

class State:
    def __init__(self):
        self.current_sample = None # Loaded Sample (Sample Object)
        self.samples = None # Dataframe of Samples (only metadata)

        self.set_samples()

####################################################################
################### LOADING AND SAVING FUNCTIONS ###################
####################################################################
    
    def load_sample(self, name):
        print('Loading sample, this can take some seconds...')
        self.current_sample = Sample(name = name)
        res, self.current_sample =  self.current_sample.load()
        if res == 0: return 0


    def set_samples(self):
        dirs = sorted(os.listdir('samples'))
        self.samples = pd.DataFrame(list(zip(dirs)), columns=['Sample'])

####################################################################
############################## UTILS ###############################
####################################################################

    def tabulate_sample(self):
        return self.current_sample.tabulate()


    def list_samples(self):
        table = tblt.tabulate(self.samples, headers = 'keys', tablefmt = 'github')
        return table


####################################################################
######################### IMAGE PROCESSING #########################
####################################################################

    def normalize(self):
        clr = Color()
        print(f'\n{clr.CYAN}Normalizing, this might take some seconds...{clr.ENDC}')
        self.current_sample = self.current_sample.load_channels_images(im_type='image')
        self.current_sample = self.current_sample.normalize()
        self.current_sample.save_channels_images(im_type='image_norm')
        self.current_sample = self.current_sample.dump_channels_images()     
        input(f'\n{clr.GREEN}Images normalized successfully! Press Enter to continue...{clr.ENDC}')

    
    def contrast(self, opt):
        clr = Color()

        if not os.path.isfile(f'samples/{self.current_sample.name}/image_norm.npz'):
            input(f'{clr.RED}Images need to be normalized first{clr.ENDC}')
            return

        self.current_sample = self.current_sample.load_channels_images(im_type='image_norm')
        if isinstance(self.current_sample.channels[opt].image_norm, np.ndarray):
            self.current_sample = self.current_sample.show_napari(function='contrast', opt = opt)
            self.current_sample = self.current_sample.contrast(opt = opt)
            self.current_sample.save_channels_images(im_type='image_cont')
        else: input(f'{clr.RED}Channel {self.current_sample.channels[opt].name} needs to be normalized first{clr.ENDC}')

        self.current_sample = self.current_sample.dump_channels_images()

####################################################################
########################## VISUALIZATION ###########################
####################################################################

    def show_napari(self, mode):
        self.current_sample.show_napari(mode)