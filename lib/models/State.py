from lib.models.Sample import Sample

class State:
    def __init__(self, sample=None):
        self.sample = sample

    
    def load_sample(self, name):
        self.sample = Sample(name = name)
        res, self.sample =  self.sample.load()
        if res == 0: return 0


    def tabulate_sample(self):
        return self.sample.tabulate()