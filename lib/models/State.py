import os
import numpy as np
import pandas as pd
import tabulate as tblt

from lib.models.Sample import Sample
from lib.Colors import Color

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
        print(f'Normalizing, this might take some minutes...')
        self.current_sample = self.current_sample.normalize()
        input(f'\n{clr.GREEN}Images normalized successfully! Press Enter to continue...{clr.ENDC}')

    
    def contrast(self, opt):
        clr = Color()
        if isinstance(self.current_sample.channels[opt].image_norm, np.ndarray):          
            self.current_sample = self.current_sample.show_napari(function='contrast', opt = opt)
            self.current_sample = self.current_sample.contrast(opt = opt)
        else:
            input(f'{clr.RED}Images need to be normalized first{clr.ENDC}')

####################################################################
########################## VISUALIZATION ###########################
####################################################################

    def show_napari(self, mode):
        self.current_sample.show_napari(mode)