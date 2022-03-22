import os
import json
import pickle as pkl


class Sample:

    def __init__(self, name=None, description=None, channels=None):
        self.name = name
        self.description = description
        self.channels = channels

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