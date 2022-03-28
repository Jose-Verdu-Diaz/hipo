import enum
import os
import numpy as np
import pandas as pd
import tabulate as tblt

import lib.utils as utils
from lib.models.Sample import Sample
from lib.models.Colors import Color

class State:
    def __init__(self, debug=False):
        self.current_sample = None # Loaded Sample (Sample Object)
        self.samples = None # Dataframe of Samples (only metadata)
        self.debug = debug

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
        self.current_sample.load_channels_images(im_type='image')
        self.current_sample = self.current_sample.normalize()
        self.current_sample.save_channels_images(im_type='image_norm')
        self.current_sample = self.current_sample.dump_channels_images()     
        input(f'\n{clr.GREEN}Images normalized successfully! Press Enter to continue...{clr.ENDC}')

    
    def contrast(self, opt):
        clr = Color()
        if not os.path.isfile(f'samples/{self.current_sample.name}/image_norm.npz'):
            input(f'{clr.RED}Images need to be normalized first. Press Enter to continue...{clr.ENDC}')
            return

        self.current_sample.load_channels_images(im_type='image_norm')
        self.current_sample.load_channels_images(im_type='image_cont')
        if isinstance(self.current_sample.channels[opt].image_norm, np.ndarray):
            print(f'{clr.CYAN}Opening Napari. Close Napari to continue...{clr.ENDC}')
            with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
                self.current_sample = self.current_sample.show_napari(function='contrast', opt = opt)
            self.current_sample = self.current_sample.contrast(opt = opt)
            self.current_sample.save_channels_images(im_type='image_cont')
            self.current_sample.update_df()
        else: 
            input(f'{clr.RED}Channel {self.current_sample.channels[opt].name} needs to be normalized first{clr.ENDC}')
            return

        self.current_sample = self.current_sample.dump_channels_images()
        input(f'\n{clr.GREEN}Contrast applied successfully! Press Enter to continue...{clr.ENDC}')

####################################################################
########################## VISUALIZATION ###########################
####################################################################

    def show_napari(self, mode):
        clr = Color()
        if type(mode) != dict: mode = {mode: True}
        for i, imt in enumerate(mode):
            if mode[imt] and imt != 'mask': 
                res = self.current_sample.load_channels_images(im_type = imt)
                if res == None:
                    input(f'{clr.RED}File for {imt} does not exist. Press Enter to continue...{clr.ENDC}')
                    return
        self.current_sample.show_napari(im_type = mode, function = 'display')
        self.current_sample = self.current_sample.dump_channels_images() 