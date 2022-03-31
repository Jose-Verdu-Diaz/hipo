import os
import gc
import numpy as np
import pandas as pd
import tkinter as tk
import tabulate as tblt
from tkinter import filedialog

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
        clr = Color()
        print(f'{clr.CYAN}Loading sample, this can take some seconds...{clr.ENDC}')
        self.current_sample = Sample(name = name)
        res, self.current_sample =  self.current_sample.load()
        if res == 0: return 0


    def set_samples(self):
        dirs = sorted(os.listdir('samples'))
        self.samples = pd.DataFrame(list(zip(dirs)), columns=['Sample'])

    def clear_current_sample(self):
        self.current_sample = None
        return self

    def dump(self):
        self.current_sample = self.current_sample.dump_channels_images()
        self.current_sample = self.current_sample.dump_fiber_labels()


    def import_labels(self):
        clr = Color()
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename()
        if path.endswith('.tiff'): res = self.current_sample.import_labels(path=path, ftype='tiff')
        elif path.endswith('.npz'): res = self.current_sample.import_labels(path=path, ftype='npz')
        else:
            input(f'{clr.RED}File type not recognised. Press Enter to continue...{clr.ENDC}')
        if res == None: input(f'{clr.RED}Labels shape do not match image shape. Press Enter to continue...{clr.ENDC}')
        else: input(f'{clr.GREEN}Labels imported successfully! Press Enter to continue...{clr.ENDC}')
        self.dump() 
        


####################################################################
############################## UTILS ###############################
####################################################################

    def create_new(self, name):
        clr = Color()
        sample = Sample(name=name)
        sample.make_dir_structure()
        self.set_samples()
        print(f'\n{clr.GREEN}Sample created successfully!{clr.ENDC}')
        input(f'\n{clr.YELLOW}Add sample files in {clr.UNDERLINE}samples/{name}/input{clr.ENDC}{clr.YELLOW}. Press Enter to continue...{clr.ENDC}')
        return self


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
        self.dump()  
        input(f'\n{clr.GREEN}Images normalized successfully! Press Enter to continue...{clr.ENDC}')

    
    def contrast(self, opt):
        clr = Color()

        res = self.current_sample.load_channels_images(im_type='image_norm')
        if res == None:
            input(f'{clr.RED}Images need to be normalized first. Press Enter to continue...{clr.ENDC}')
            return

        self.current_sample.load_channels_images(im_type='image_cont')
        if isinstance(self.current_sample.channels[opt].image_norm, np.ndarray):

            if str(input('Use napari for selecting a percentile? (y/n)')) == 'y':
                with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
                    self.current_sample = self.current_sample.show_napari(function='contrast', opt = opt)
            else:
                low_p = float(input('Select a lower quantile: '))
                top_p = float(input('Select a top quantile: '))
                self.current_sample.channels[opt].contrast_limits = (low_p, top_p)

            self.current_sample = self.current_sample.contrast(opt = opt)
            self.current_sample.save_channels_images(im_type='image_cont')
            self.current_sample.update_df()
        else: 
            input(f'{clr.RED}Channel {self.current_sample.channels[opt].name} needs to be normalized first{clr.ENDC}')
            return

        self.dump() 
        input(f'\n{clr.GREEN}Contrast applied successfully! Press Enter to continue...{clr.ENDC}')


    def threshold(self, opt):
        clr = Color()
        if not os.path.isfile(f'samples/{self.current_sample.name}/image_cont.npz'):
            input(f'{clr.RED}The file image_cont.npz does not exist. Apply a contrast to some images first. Press Enter to continue...{clr.ENDC}')
            return

        self.current_sample.load_channels_images(im_type='image_cont')
        self.current_sample.load_channels_images(im_type='image_thre')
        if isinstance(self.current_sample.channels[opt].image_cont, np.ndarray):
            with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
                self.current_sample = self.current_sample.show_napari(function='threshold', opt = opt)
            self.current_sample = self.current_sample.threshold(opt = opt)
            self.current_sample.save_channels_images(im_type='image_thre')
            self.current_sample.update_df()
        else: 
            input(f'{clr.RED}Channel {self.current_sample.channels[opt].name} needs a contrast modification first{clr.ENDC}')
            return

        self.dump() 
        input(f'\n{clr.GREEN}Threshold applied successfully! Press Enter to continue...{clr.ENDC}')

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
                    input(f'{clr.RED}File {imt}.npz does not exist. Press Enter to continue...{clr.ENDC}')
                    return                
        with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
            self.current_sample.show_napari(im_type = mode, function = 'display')
        self.dump() 
        gc.collect()


    def show_segmentation(self):
        clr = Color()
        res = self.current_sample.load_channels_images(im_type = 'image_cont')
        if res == None:
            input(f'{clr.RED}File image_cont.npz does not exist. Press Enter to continue...{clr.ENDC}')
            return
        res = self.current_sample.load_fiber_labels()
        if res == None:
            input(f'{clr.RED}File fiber_labels.npz does not exist, segment fibers first. Press Enter to continue...{clr.ENDC}')
            return
        with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
            res = self.current_sample.show_napari(function='fiber_labels')
        if res == None:
            input(f'{clr.RED}Channel  Tm(169) needs a contrast modification first. Press Enter to continue...{clr.ENDC}')
            return            


####################################################################
############################ ANALYSIS ##############################
####################################################################

    def analyse(self):
        clr = Color()
        print(f'\n{clr.CYAN}Analyzing, this might take some seconds...{clr.ENDC}')
        res = self.current_sample.load_channels_images(im_type = 'image_thre')
        if res == None:
            input(f'{clr.RED}File image_thre.npz does not exist, threshold some images first. Press Enter to continue...{clr.ENDC}')
            return
        self.current_sample.analyse()
        self.dump() 
        print(f'\n{clr.GREEN}Images analyzed successfully! Press Enter to continue...{clr.ENDC}')
        input(f'{clr.GREEN}Output at samples/{self.current_sample.name}/analysis.csv Press Enter to continue...{clr.ENDC}')

    
    def segment_fibers(self): 
        clr = Color()
        print(f'\n{clr.CYAN}Segmenting, this might take some seconds...{clr.ENDC}')
        res = self.current_sample.load_channels_images(im_type = 'image_thre')
        if res == None:
            input(f'{clr.RED}File image_thre.npz does not exist, threshold channel Tm(169) first. Press Enter to continue...{clr.ENDC}')
            return
        with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
            res = self.current_sample.segment_fibers()
        self.dump() 
        if res == None:
            input(f'{clr.RED}Channel Tm(169) has to be thresholded first. Press Enter to continue...{clr.ENDC}')
        else:
            input(f'\n{clr.GREEN}Fibers segmented successfully! Press Enter to continue...{clr.ENDC}')