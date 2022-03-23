import os
import json
import pandas as pd
import pickle as pkl
import tifffile as tf

from lib.Colors import Color
import lib.consistency as consistency
from lib.models.Channel import Channel



class Sample:

    def __init__(self, name=None, description=None, channels=None, summary=None, mask=None):
        self.name = name
        self.description = description
        self.channels = channels
        self.summary = summary
        self.mask = mask

    def make_dir_structure(self):
        '''Creates the directory and file structure for a new sample
        '''

        path = f'samples/{self.name}'
        os.makedirs(path)

        with open('lib/json/sample_dir_structure.json', 'r') as f: data = json.load(f)
        for d in data: os.makedirs(f'{path}/{d}')

        self.save()


    def save(self):
        path = f'samples/{self.name}'
        with open(f'{path}/list.pkl', 'wb') as file: pkl.dump(self, file)

    
    def load(self):
        path = f'samples/{self.name}'
        with open(f'{path}/list.pkl', 'rb') as file: self = pkl.load(file)
        res = self.load_channels()

        return res

    
    def load_channels(self):
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

                images, channels, labels, self.summary = self.parse_tiff(tiff_file, txt_file)

                df = pd.DataFrame(
                        list(zip(images, channels, labels)),
                        columns =['Image', 'Channel', 'Label']
                    ).sort_values(['Channel']).reset_index(drop=True)

                self.channels = []
                for i,c in enumerate(df['Channel'].to_list()): 
                    self.channels.append(Channel(name=c, label=df['Label'].to_list()[i], image=df['Image'].to_list()[i]))

                self.save()

                return 1


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

            label =str(summary_df['Label'][slice])
            labels.append(label if not label == 'nan' else '-')

        return tiff_slices, channels, labels, summary_df


    def sample_df():
        '''Generate a table with the information of a sample

        Returns
        -------
        table
            Printable string table with the information of the sample and a header
        df
            Pandas DataFrame containing information of the sample
        '''

        color = Color()

        img_sizes = [img.shape for img in images]
        pixel_min = self.summary['MinValue'].tolist()
        pixel_max = self.summar['MaxValue'].tolist()
        with open(f'samples/{self.name}/{self.name}.json', 'r') as f: data = json.load(f)
        channel_threshold = ['-' if c['threshold'] == None else c['threshold'] for c in data['channels']]
        channel_contrast = ['-' if c['contrast_limits'] == None else c['contrast_limits'] for c in data['channels']]


        for c in self.channels: pass


        df = pd.DataFrame(
                list(zip(images, metals, labels, img_sizes, pixel_min, pixel_max)),
                columns =['Image', 'Channel', 'Label', 'Image Size', 'Min', 'Max']
            )

        df = df.sort_values(['Channel']).reset_index(drop=True)

        df['Th.'] = channel_threshold # channel_threshold is already sorted, add it after sorting DataFrame
        df['Cont.'] = channel_contrast # channel_contrast is already sorted, add it after sorting DataFrame

        table = tabulate(df.loc[:, df.columns != 'Image'], headers = 'keys', tablefmt = 'github')
        table = f'{color.BOLD}{color.UNDERLINE}Displaying sample:{color.ENDC} {self.name}\n\n{table}'

        return table, df