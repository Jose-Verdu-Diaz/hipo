import os
import pandas as pd
import tabulate as tblt

from lib.models.Sample import Sample

class State:
    def __init__(self):
        self.current_sample = None # Loaded Sample (Sample Object)
        self.samples = None # Dataframe of Samples (only metadata)

        self.set_samples()

    
    def load_sample(self, name):
        self.current_sample = Sample(name = name)
        res, self.current_sample =  self.current_sample.load()
        if res == 0: return 0


    def tabulate_sample(self):
        return self.current_sample.tabulate()


    def set_samples(self):
        dirs = sorted(os.listdir('samples'))
        self.samples = pd.DataFrame(list(zip(dirs)), columns=['Sample'])


    def list_samples(self):
        table = tblt.tabulate(self.samples, headers = 'keys', tablefmt = 'github')
        return table