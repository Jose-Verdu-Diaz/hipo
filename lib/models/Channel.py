class Channel:

    def __init__(self, name=None, label=None, image=None, threshold=None, contrast_limits=None):
        self.name = name
        self.label = label
        self.image = image
        self.threshold = threshold
        self.contrast_limits = contrast_limits
        