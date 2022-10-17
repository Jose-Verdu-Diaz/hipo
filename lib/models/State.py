import os
import gc
import pandas as pd
import tkinter as tk
import seaborn as sns
import tabulate as tblt
from tkinter import filedialog
import matplotlib.pyplot as plt

import lib.utils as utils
from lib.models.Colors import Color
from lib.models.Sample import Sample
from lib.image import segment_points


class State:
    def __init__(self, debug=False):
        self.current_sample = None # Loaded Sample (Sample Object)
        self.samples = None # Dataframe of Samples (only metadata)
        self.debug = debug

        self.set_samples()

####################################################################
################### LOADING AND SAVING FUNCTIONS ###################
####################################################################
    
    def load_sample(self, name, txt_path=None, geojson_path=None, tiff_path=None):
        clr = Color()
        print(f'{clr.CYAN}Loading sample, this can take some seconds...{clr.ENDC}')
        self.current_sample = Sample(name = name)
        res, self.current_sample =  self.current_sample.load(txt_path, geojson_path, tiff_path)
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

        if name in self.samples['Sample'].to_list():
            input(f'\n{clr.RED}A sample with the same name already exists. Press Enter to continue...{clr.ENDC}')
        else:
            root = tk.Tk()
            root.withdraw()
            print(f'\n{clr.YELLOW}Select the summary (.txt) file{clr.ENDC}')
            txt_path = filedialog.askopenfilename(filetypes=[('text file', '*.txt')])
            print(f'\n{clr.YELLOW}Select the roi (.geojson) file{clr.ENDC}')
            geojson_path = filedialog.askopenfilename(filetypes=[('roi file', '*.geojson')])
            print(f'\n{clr.YELLOW}Select the image (.tiff) file{clr.ENDC}')
            tiff_path = filedialog.askopenfilename(filetypes=[('image file', '*.tiff')])

            if os.path.isfile(txt_path) and os.path.isfile(geojson_path) and os.path.isfile(tiff_path): pass
            else: 
                input(f'\n{clr.RED}There was a problem loading the input files. Press Enter to continue...{clr.ENDC}')
                return self

            sample = Sample(name=name)
            sample.make_dir_structure()
            self.set_samples()
            print(f'\n{clr.GREEN}Sample created successfully!{clr.ENDC}')

            self.load_sample(name, txt_path, geojson_path, tiff_path)
            self.dump()

        return self


    def tabulate_sample(self, header=True):
        return self.current_sample.tabulate(header)


    def list_samples(self):
        table = tblt.tabulate(self.samples, headers = 'keys', tablefmt = 'github')
        return table


####################################################################
######################### IMAGE PROCESSING #########################
####################################################################

    def point_segm(self, opt:int):
        clr = Color()
        if not os.path.isfile(f'samples/{self.current_sample.name}/image.npz'):
            input(f'{clr.RED}The file image.npz does not exist. Press Enter to continue...{clr.ENDC}')
            return

        self.current_sample.load_channels_images(im_type='image', options=opt)
        with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
            img = self.current_sample.napari_display(options = [opt], point_segm=True, mask=True)

        points = segment_points(img)
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        a = [p[2] for p in points]
        self.current_sample.channels[opt].points = pd.DataFrame(list(zip(range(len(x)), x, y, a)), columns=['index', 'axis-0', 'axis-1', 'area'])

        with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
            res = self.current_sample.napari_display(options = [opt], mask=True, point_filter=True)

        #with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
        #    res = self.current_sample.napari_display(options = [opt], mask=True)

        self.current_sample.update_df()
        self.current_sample.save_points(opt)
        self.current_sample.save()
        self.dump()



    def threshold(self, opt: int):
        clr = Color()
        if not os.path.isfile(f'samples/{self.current_sample.name}/image.npz'):
            input(f'{clr.RED}The file image.npz does not exist. Press Enter to continue...{clr.ENDC}')
            return

        self.current_sample.load_channels_images(im_type='image', options=opt)
        if utils.input_yes_no(txt='Use napari for selecting a percentile?'):
            with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
                self.current_sample = self.current_sample.napari_display(options = [opt], mask=True, threshold=True)
        else:
            max = self.current_sample.channels[opt].apply_mask(self.current_sample.mask).max()
            th = utils.input_number(f'Enter a threshold (between 0 and {max})', cancel = False, range = (0, max), type = 'float')
            self.current_sample.channels[opt].th = th

        self.current_sample.update_df()
        self.dump() 
        input(f'\n{clr.GREEN}Threshold modified successfully! Press Enter to continue...{clr.ENDC}')

####################################################################
########################## VISUALIZATION ###########################
####################################################################

    def show_napari(self, options: dict):
        clr = Color()

        channels = []
        for opt in options: 
            if options[opt] and opt not in ['m', 'l']: channels.append(opt)
        if len(channels) > 0: 
            res = self.current_sample.load_channels_images(options = channels)
            if res == None:
                input(f'{clr.RED}File {opt}.npz does not exist. Press Enter to continue...{clr.ENDC}')
                self.dump() 
                return
        if options['m']: channels.append('m')
        if options['l']: 
            channels.append('l')
            res = self.current_sample.load_fiber_labels()
            if res == None:
                input(f'{clr.RED}File fiber_labels.npz does not exist, segment fibers first. Press Enter to continue...{clr.ENDC}')
                self.dump() 
                return

        with utils.suppress_output(suppress_stdout=not self.debug, suppress_stderr=not self.debug):
            self.current_sample.napari_display(options = channels, screenshot=True)

        self.dump() 
        gc.collect()         

####################################################################
############################ ANALYSIS ##############################
####################################################################

    def analyse(self):
        clr = Color()
        print(f'\n{clr.CYAN}Analyzing, this might take some seconds...{clr.ENDC}')
        res = self.current_sample.load_channels_images(im_type = 'image')
        if res == None:
            input(f'{clr.RED}File image.npz does not exist. Press Enter to continue...{clr.ENDC}')
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

####################################################################
############################## EDIT ################################
####################################################################

    def change_name(self, name):
        clr = Color()

        if name in self.samples['Sample'].to_list():
            input(f'\n{clr.RED}A sample with the same name already exists. Press Enter to continue...{clr.ENDC}')
        else:
            sample = Sample(name=name)
            os.rename(f'samples/{self.current_sample.name}', f'samples/{name}')
            self.current_sample.name = name
            self.current_sample.save()
            self.set_samples()
            input(f'\n{clr.GREEN}Sample created successfully! Press Enter to continue...{clr.ENDC}')
        return self