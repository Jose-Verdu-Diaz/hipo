import os
import gc
import json
import napari
import numpy as np
import pandas as pd
import pickle as pkl
from tqdm import tqdm
import tifffile as tf
import tabulate as tblt
from magicgui import magicgui
from napari.layers import Points
from PIL import Image, ImageDraw
from datetime import datetime as dtm
from skimage.filters._gaussian import gaussian
from napari.types import ImageData, LayerDataTuple
from skimage.filters.thresholding import threshold_otsu

from lib.models.Colors import Color
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

    def save_points(self, opt:int=None):
        if isinstance(opt, int) and hasattr(self.channels[opt], 'points') and not self.channels[opt].points.empty:
            os.makedirs(f'samples/{self.name}/points/', exist_ok=True)
            self.channels[opt].points.to_csv(f'samples/{self.name}/points/{self.name}_{self.channels[opt].label}_points.csv')

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

    
    def load(self, txt_path=None, geojson_path=None, tiff_path=None):
        path = f'samples/{self.name}'
        with open(f'{path}/sample.pkl', 'rb') as file: self = pkl.load(file)
        res = self.create_channels(txt_path, geojson_path, tiff_path)

        return res, self

    
    def create_channels(self, txt_path=None, geojson_path=None, tiff_path=None):
        if self.channels == None:
            clr = Color()

            if txt_path == None or geojson_path == None or tiff_path == None:
                    input(f'{clr.RED}No input files found. Press Enter to continue...{clr.ENDC}')
                    return 0

            while True: # Is his really needed???
                images, channels, labels, summary = self.parse_tiff(tiff_path, txt_path)

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
                self.make_mask(geojson_path)   
                self.save()
                self.update_df()

                return 1


    def load_channels_images(self, im_type = 'image', options = None):
        clr = Color()
        if os.path.isfile(f'samples/{self.name}/{im_type}.npz'):
            img_stack = np.load(f'samples/{self.name}/{im_type}.npz')
        else: return None

        if isinstance(options, int): 
            print(f'{clr.GREY}Loading {im_type}...{clr.ENDC}')
            self.channels[options] = self.channels[options].load_images(im_type=im_type, img=img_stack[self.channels[options].name])
        elif isinstance(options, list): 
            for opt in tqdm(options, desc = f'{clr.GREY}Loading selected channels', postfix=clr.ENDC):
                self.channels[opt] = self.channels[opt].load_images(im_type=im_type, img=img_stack[self.channels[opt].name]) 
        else:
            for c in tqdm(self.channels, desc = f'{clr.GREY}Loading {im_type}', postfix=clr.ENDC):
                if c.name in img_stack.keys():
                    c = c.load_images(im_type=im_type, img=img_stack[c.name])        
        return self


    def load_fiber_labels(self):
        clr = Color()
        print(f'{clr.GREY}Loading fiber labels...{clr.ENDC}')
        if os.path.isfile(f'samples/{self.name}/fiber_labels.npz'):
            self.fiber_labels = np.load(f'samples/{self.name}/fiber_labels.npz')['arr_0']
        else: return None
        return self


    def import_labels(self, path, ftype):
        clr = Color()
        print(f'{clr.GREY}Importing lables...{clr.ENDC}')
        if ftype == 'tiff':
            labels = tf.TiffFile(path).asarray()
        elif ftype == 'npz':
            labels = np.load(path)['arr_0']

        if labels.shape == self.img_size:
            self.fiber_labels = labels
            np.savez_compressed(f'samples/{self.name}/fiber_labels.npz', self.fiber_labels)
            return self
        else: return None
        

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
        if self.channels != None:
            clr = Color()

            pixel_min = self.summary['MinValue'].tolist()
            pixel_max = self.summary['MaxValue'].tolist()

            names, labels, thresholds, points = [], [], [], []

            for c in self.channels:
                names.append(c.name)
                labels.append(c.label)
                thresholds.append('-' if c.th == None else c.th)
                points.append('-' if not hasattr(c, 'points') or c.points.empty else len(c.points))

            self.df = pd.DataFrame(
                    list(zip(names, labels, pixel_min, pixel_max, thresholds, points)),
                    columns =['Channel', 'Label', 'Min', 'Max', 'Th.', '# points']
                )

            self.save()

            return self.df

####################################################################
############################## UTILS ###############################
####################################################################

    def tabulate(self, header=True):
        if isinstance(self.df, pd.DataFrame):
            clr = Color()
            table = tblt.tabulate(self.df, headers = 'keys', tablefmt = 'github')
            if header: table = f'{clr.BOLD}{clr.UNDERLINE}Displaying sample:{clr.ENDC} {self.name}\n\n{table}'
            return table

####################################################################
######################### IMAGE PROCESSING #########################
####################################################################

    def make_mask(self, geojson_file):
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


    def apply_mask(self, mask, img):
        return np.where(mask, img, 0)

    
    def threshold(self, opt = 0):
        self.channels[opt] = self.channels[opt].threshold()
        return self

####################################################################
########################## VISUALIZATION ###########################
####################################################################

    def napari_display(self, options: list=[], mask=False, threshold=False, screenshot=False, point_segm=False, point_filter=False):
        '''Shows images in napari and performs screenshotting and thresholding

        Parameters
        ----------
        options, optional
            List of images to show, by default []
            Channel images are represented by its index (int) in slef.channels
            The mask image is represented by the string 'm'
            The fiber labels image is represented by the string 'l'
        mask, optional
            Apply the mask to the images, by default False
        threshold, optional
            Show the threshold selector and return a threshold, by default False
            If True, only one image can be selected ( len(options)==1 )
        '''

        clr = Color()

        if (threshold or point_segm or point_filter) and not len(options) == 1 and not isinstance(options[0], int):
            input(f'{clr.RED}Only one channel can be selected if threshold=True. Press Enter to continue...{clr.ENDC}')
            return self

        viewer = napari.Viewer()

        layers = []
        for opt in options:
            if opt == 'm': layers.append(viewer.add_image(self.mask, name = 'Mask', opacity=0.25, blending='additive'))
            elif opt == 'l':
                if mask: l = self.apply_mask(mask=self.mask, img=self.fiber_labels)
                else: l = self.fiber_labels
                layers.append(viewer.add_labels(l, name = 'Fiber Labels', opacity=0.25, blending='additive'))
            else:
                if mask: l = self.channels[opt].apply_mask(self.mask)
                else: l = self.channels[opt].image                           
                layers.append(viewer.add_image(l, name = self.channels[opt].label, blending='additive', contrast_limits=[0, l.max()]))
                # use hasattr for compatibility with older HIPO versions
                if hasattr(self.channels[opt], 'points') and not self.channels[opt].points.empty:
                    df = self.channels[opt].points
                    l = [[x, y] for x, y in zip(list(df['axis-0']), list(df['axis-1']))]
                    a =  list(df['area'])
                    layers.append(viewer.add_points(l, features={'area':a}, name = f'{self.channels[opt].label} Points', face_color='red', edge_color='red', opacity=0.5))

        if screenshot:
            @magicgui(
                call_button='Screenshot',
                spn={'widget_type': 'FloatSpinBox', 'min': 1, 'max': 10, 'label': 'Scale'},
                layout='horizontal'
            )
            def screenshot(spn: float):
                if not os.path.isdir(f'samples/{self.name}/screenshots'): os.makedirs(f'samples/{self.name}/screenshots')
                viewer.screenshot(path=f'samples/{self.name}/screenshots/{dtm.now().strftime("%Y-%m-%d-%H-%M-%S")}.tiff', scale=spn)
            viewer.window.add_dock_widget(screenshot, area='bottom')

        if threshold:
            @magicgui(
                auto_call=True,
                p={'widget_type': 'FloatSlider', 'max': 100, 'min': 70, 'step': 1, 'label': 'Percentile'},
                a={'widget_type': 'SpinBox', 'max': layers[0].data.max(), 'min': 0, 'label': 'Absolute'},
                mode={'choices': ['percentile', 'absolute']},
                layout='horizontal'
            )
            def threshold(data: ImageData, p: float, a: int, mode='percentile') -> ImageData:
                if mode == 'percentile':
                    th = np.percentile(data, p)
                elif mode == 'absolute': th = a
                layers[0].metadata['threshold'] = str(th)
                return np.where(data < th, 0, data)
            viewer.window.add_dock_widget(threshold, area='bottom')

        if point_segm:
            @magicgui(
                auto_call=True,
                p={'widget_type': 'FloatSlider', 'max': 100, 'min': 97, 'step': 0.1, 'label': 'Percentile'},
                s={'widget_type': 'FloatSlider', 'max': 3, 'min': 0, 'label': 'Sigma'},
                mode={'choices': ['None', 'Otsu']},
                layout='horizontal'
            )
            def cont_blur_thresh(data: ImageData, p: float, s: float, mode='None') -> LayerDataTuple:
                u = np.percentile(data, p)
                _data = data / u
                _data = np.where(_data < 1, _data, 1)
                _data = np.array(_data * 255, dtype='uint8')
                _data = gaussian(_data, sigma=s)
                if mode == 'None': res = _data
                if mode == 'Otsu': res = _data > threshold_otsu(_data)
                return (res, {'name': 'Result', 'contrast_limits': [0, res.max()]})
            viewer.window.add_dock_widget(cont_blur_thresh, area='bottom')


        if point_filter:
            # Waiting for magic gui to implement a range slider. Use 2 sliders for the moment
            # https://forum.image.sc/t/getting-a-range-slider-on-napari/51728
            @magicgui(
                auto_call=True,
                min={'widget_type': 'Slider', 'max': 100, 'min': 0, 'value': 0, 'step': 1, 'label': 'Min. Area'},
                max={'widget_type': 'Slider', 'max': 100, 'min': 0, 'value': 100, 'step': 1, 'label': 'Max. Area'},
                layout='horizontal'
            )
            def filter_area(layer: Points, min: int, max: int) -> LayerDataTuple:
                a_min = np.percentile(list(layer.features['area']), min)
                a_max = np.percentile(list(layer.features['area']), max)
                idx = layer.features.index[(layer.features['area'] >= a_min) & (layer.features['area'] <= a_max)].tolist()
                res = layer.data[idx]
                return (
                        res, 
                        {
                            'name': 'Result', 
                            'symbol': 'cross', 
                            'face_color': 'blue', 
                            'edge_color': 'transparent',
                            'features': {
                                'area': list(layer.features[(layer.features['area'] >= a_min) & (layer.features['area'] <= a_max)])
                            }
                        }, 
                        'points'
                    )
            viewer.window.add_dock_widget(filter_area, area='bottom')


        print(f'{clr.CYAN}Opening Napari. Close Napari to continue...{clr.ENDC}')
        napari.run()

        if threshold: self.channels[options[0]].th = layers[0].metadata['threshold']
        elif point_segm: return viewer.layers['Result'].data
        elif point_filter: return viewer.layers['Result']


        for l in layers: del(l)
        del(layers)
        gc.collect()

        return self
        


####################################################################
############################ ANALYSIS ##############################
####################################################################

    def analyse(self):
        result = []
        for c in self.channels:
            if isinstance(getattr(c, 'image'), np.ndarray) and c.th != None:
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