import os
import gc
import sys
import json
import napari
import numpy as np
import pandas as pd
import pickle as pkl
from tqdm import tqdm
import tifffile as tf
import tabulate as tblt
from magicgui import magicgui
from PIL import Image, ImageDraw
from napari.types import ImageData
from napari_brightness_contrast._dock_widget import BrightnessContrast

from lib.models.Colors import Color
import lib.consistency as consistency
from lib.models.Channel import Channel



class Sample:

    def __init__(self, name=None, description=None, channels=None, summary=None, mask=None):
        self.name = name
        self.description = description
        self.channels = channels
        self.summary = summary
        self.mask = mask
        self.fiber_labels = None
        self.df = None
        self.img_size = None

####################################################################
################### LOADING AND SAVING FUNCTIONS ###################
####################################################################

    def make_dir_structure(self):
        '''Creates the directory and file structure for a new sample
        '''

        path = f'samples/{self.name}'
        os.makedirs(path)

        with open('lib/json/sample_dir_structure.json', 'r') as f: data = json.load(f)
        for d in data: os.makedirs(f'{path}/{d}')

        self.save()


    def save(self):
        '''Stores a pickle file with the Sample object

        Stores the current Sample object as a pickle binary file. Removes the channel
        images before creating the file, as they make the binary file extremely large.
        These images should be stored in compressed numpy binary files using the 
        save_channels_images() method.
        '''

        clr = Color()
        print(f'{clr.GREY}Saving sample, this can take some seconds...{clr.ENDC}')
        self.dump_channels_images()
        path = f'samples/{self.name}'
        with open(f'{path}/sample.pkl', 'wb') as file: pkl.dump(self, file)

    
    def load(self):
        path = f'samples/{self.name}'
        with open(f'{path}/sample.pkl', 'rb') as file: self = pkl.load(file)
        res = self.create_channels()

        return res, self

    
    def create_channels(self):
        if self.channels == None:
            clr = Color()

            while True:
                path = f'samples/{self.name}/input'

                try: 
                    result = consistency.check_input_files(self.name)
                    if not result is None: raise result

                except Exception as e: 
                    input(f'{clr.RED}{e} Press Enter to continue...{clr.ENDC}')
                    return 0           

                files = os.listdir(path)

                geojson_file, txt_file, tiff_file = '','',''

                for f in files:
                    path = f'samples/{self.name}/input/{f}'
                    if f.endswith('.txt'): txt_file = path
                    elif f.endswith('.tiff'): tiff_file = path
                    elif f.endswith('.geojson'): geojson_file = path

                images, channels, labels, summary = self.parse_tiff(tiff_file, txt_file)

                self.img_size = images[0].shape # We assume the same size for all input images

                self.summary = summary.sort_values(['Channel']).reset_index(drop=True) 

                df = pd.DataFrame(
                        list(zip(images, channels, labels)),
                        columns =['Image', 'Channel', 'Label']
                    ).sort_values(['Channel']).reset_index(drop=True)

                self.channels = []
                for i,c in enumerate(df['Channel'].to_list()): 
                    self.channels.append(Channel(name=c, label=df['Label'].to_list()[i], image=df['Image'].to_list()[i]))

                self.save_channels_images(im_type='image')
                self.make_mask(geojson_file)      
                self.save()
                self.update_df()

                return 1


    def load_channels_images(self, im_type = 'image'):
        clr = Color()
        if os.path.isfile(f'samples/{self.name}/{im_type}.npz'):
            img_stack = np.load(f'samples/{self.name}/{im_type}.npz')
        else: return None
        for c in tqdm(self.channels, desc = f'{clr.GREY}Loading {im_type}', postfix=clr.ENDC):
            if c.name in img_stack.keys():
                c = c.load_images(im_type=im_type, img=img_stack[c.name])        
        return self


    def load_fiber_labels(self):
        clr = Color()
        print(f'{clr.GREY}Loading fiber lables...{clr.ENDC}')
        if os.path.isfile(f'samples/{self.name}/fiber_labels.npz'):
            self.fiber_labels = np.load(f'samples/{self.name}/fiber_labels.npz')['arr_0']
        else: return None
        return self


    def save_channels_images(self, im_type = None):
        '''Saves channel images in compressed numpy binary files (.npz)

        This method provides a way of storing channel images in a compressed format,
        allowing for a more compact file system. All images or a single image type
        can be stored using the im_type parameter.

        Parameters
        ----------
        im_type, optional
            Type of image to store. Options are 'image', 'image_norm', 'image_cont'
            and None. If None, all image types are stored. By default None
        '''

        if self.channels != None:
            clr = Color()
            IM_TYPE_OPT = ['image', 'image_norm', 'image_cont']
            save_list = [im_type] if im_type != None else IM_TYPE_OPT
            for s in save_list:
                images = {}
                for c in tqdm(self.channels, desc = f'{clr.GREY}Saving {s}', postfix=clr.ENDC): 
                    if isinstance(getattr(c, s), np.ndarray): images[c.name] = getattr(c, s) 
                print(f'{clr.GREY}Compressing images file...{clr.ENDC}')
                np.savez_compressed(f'samples/{self.name}/{s}.npz', **images)


    def parse_tiff(self, tiff_path, summary_path):
        '''Parses a hyperion tiff file with multiple images

        Parameters
        ----------
        tiff_path
            Path of tiff file
        summary_path
            Path to summary file

        Returns
        -------
        tiff_slices
            Numpy array of images
        channels
            List of channels
        labels
            List of labels
        summary_df
            Pandas DataFrame with the data of the summary file
        '''

        tiff_slices = tf.TiffFile(tiff_path).asarray()
        channels, labels = [], []

        summary_df = pd.read_csv(summary_path, sep = '\t')

        for slice in range(tiff_slices.shape[0]):
            channels.append(str(summary_df['Channel'][slice]))

            label = str(summary_df['Label'][slice])
            labels.append(label if not label == 'nan' else '-')

        return tiff_slices, channels, labels, summary_df


    def dump_channels_images(self):
        if self.channels != None:
            clr = Color()
            for c in tqdm(self.channels, desc = f'{clr.GREY}Dumping channel images', postfix=clr.ENDC): c = c.dump_images()
        return self

    def dump_fiber_labels(self):
        self.fiber_labels = None
        return self

    def update_df(self):
        '''Generate a table with the information of a sample

        Returns
        -------
        table
            Printable string table with the information of the sample and a header
        df
            Pandas DataFrame containing information of the sample
        '''

        if self.channels != None:
            clr = Color()

            pixel_min = self.summary['MinValue'].tolist()
            pixel_max = self.summary['MaxValue'].tolist()

            names, labels, thresholds, contrasts= [], [], [], []

            for c in self.channels:
                names.append(c.name)
                labels.append(c.label)
                thresholds.append('-' if c.th == None else c.th)
                contrasts.append('-' if c.contrast_limits == None else c.contrast_limits)

            self.df = pd.DataFrame(
                    list(zip(names, labels, pixel_min, pixel_max, thresholds, contrasts)),
                    columns =['Channel', 'Label', 'Min', 'Max', 'Th.', 'Cont.']
                )

            self.save()

            return self.df

####################################################################
############################## UTILS ###############################
####################################################################

    def tabulate(self):
        if isinstance(self.df, pd.DataFrame):
            clr = Color()
            table = tblt.tabulate(self.df, headers = 'keys', tablefmt = 'github')
            table = f'{clr.BOLD}{clr.UNDERLINE}Displaying sample:{clr.ENDC} {self.name}\n\n{table}'
            return table

####################################################################
######################### IMAGE PROCESSING #########################
####################################################################

    def make_mask(self, geojson_file):
        '''Creates mask images from coordinates tuples list

        Parameters
        ----------
        geojson_file
            path to geojson
        size
            Size of the mask

        Returns
        -------
            Numpy array representing the mask
        '''

        with open(geojson_file) as f: annotation_data = json.load(f)

        black = Image.new('1', Image.fromarray(self.channels[0].image).size)
        imd = ImageDraw.Draw(black)

        for ann in annotation_data["features"]:

            blob = ann["geometry"]

            if blob["type"] == "LineString": coords = blob["coordinates"]
            if blob["type"] == "Polygon": coords = blob["coordinates"][0]

            tuples = [tuple(coord) for coord in coords]
            imd.polygon(tuples,fill="white",outline="white")

        self.mask = np.array(black)


    def normalize(self):
        clr = Color()
        for c in tqdm(self.channels, desc = f'{clr.GREY}Normalizing images', postfix=clr.ENDC): c = c.normalize(self.mask)
        return self


    def contrast(self, opt = 0):
        self.channels[opt] = self.channels[opt].contrast()
        return self

    
    def threshold(self, opt = 0):
        self.channels[opt] = self.channels[opt].threshold()
        return self

####################################################################
########################## VISUALIZATION ###########################
####################################################################

    def show_napari(self, im_type = 'image', function = 'display', opt = 0):
        clr = Color()  
        viewer = napari.Viewer()

        # Open napari to obtain a threshold for a single image
        if function == 'threshold':
            img = self.channels[opt].image_cont
            layer = viewer.add_image(img)
            layer.metadata['threshold'] = 0

            @magicgui(
                auto_call=True,
                th={'widget_type': 'FloatSlider', 'max': 1},
                layout='horizontal'
            )
            def threshold(data: ImageData, th: float = 0) -> ImageData:
                layer.metadata['threshold'] = th
                return np.where(data > th, data, 0)

            viewer.window.add_dock_widget(threshold, area='bottom')

        # Open napari to obtain a contrast for a single image
        elif function == 'contrast':
            layer = viewer.add_image(self.channels[opt].image_norm)
            
            bc = BrightnessContrast(viewer)
            viewer.window.add_dock_widget(bc)

            # Store new percentile values on update
            layer.metadata = {
                'percentile_upper': bc.spinner_upper_percentile.value(),
                'percentile_lower': bc.spinner_lower_percentile.value()
            }
            def update(event):
                layer.metadata = {
                    'percentile_upper': bc.spinner_upper_percentile.value(),
                    'percentile_lower': bc.spinner_lower_percentile.value()
                }
            
            layer.events.connect(callback=update)

        # Open napari to display a stack of images
        elif function == 'display':
            NAMES = {
                'image': 'Raw',
                'image_norm': 'Norm.',
                'image_cont': 'Cont.',
                'image_thre': 'Thre.'
            }

            if type(im_type) != dict: im_type = {im_type: True}
            layers = []
            for i, imt in enumerate(im_type):
                if im_type[imt]:
                    if imt == 'mask':
                        layers.append(viewer.add_image(self.mask, name = 'Mask'))
                    else:                              
                        layers.append(viewer.add_image(np.stack([getattr(c, imt) if isinstance(getattr(c, imt), np.ndarray) else np.zeros(shape = self.img_size) for c in self.channels ]), name = imt))
                        layers[-1].metadata['type'] = imt
                        layers[-1].metadata['ch_names'] = [c.name if isinstance(getattr(c, imt), np.ndarray) else 'NaN' for c in self.channels]
                        #del(images)
                        #del(names)

                        @viewer.dims.events.current_step.connect
                        def _on_change(event):
                            idx = event.value[0]
                            for l in layers:
                                if l.name != 'Mask':
                                    l.name = f'{NAMES[l.metadata["type"]]}-{l.metadata["ch_names"][idx]}'


        elif function == 'fiber_labels':
            for c in self.channels:
                if c.name == 'Tm(169)':
                    if isinstance(getattr(c, 'image_cont'), np.ndarray): break
                    else: return None

            viewer.add_image(c.image_cont, name = 'Image')
            viewer.add_labels(self.fiber_labels, name = 'Fibers')
                 
        else:
            return None

        print(f'{clr.CYAN}Opening Napari. Close Napari to continue...{clr.ENDC}')
        napari.run()

        # Return threshold
        if function == 'threshold':
            self.channels[opt].th = layer.metadata['threshold']
            return self

        # Return contrast
        elif function == 'contrast':
            self.channels[opt].contrast_limits = (layer.metadata['percentile_lower'], layer.metadata['percentile_upper'])
            return self

        elif function == 'display':
            for l in layers: del(l)
            del(layers)
            gc.collect()

        elif function == 'fiber_labels': 
            return 1

####################################################################
############################ ANALYSIS ##############################
####################################################################

    def analyse(self):
        result = []
        for c in self.channels:
            if isinstance(getattr(c, 'image_thre'), np.ndarray):
                result.append(c.analyse(self.mask))
        result_df = pd.DataFrame(result)
        result_df.to_csv(f'samples/{self.name}/analysis.csv', index=False)


    def segment_fibers(self): 
        for c in self.channels:
            if c.name == 'Tm(169)':
                if isinstance(getattr(c, 'image_thre'), np.ndarray):
                    labels = c.segment_fibers(self.mask)
                    break
                else:
                    return None
        np.savez_compressed(f'samples/{self.name}/fiber_labels.npz', labels)
        return 1