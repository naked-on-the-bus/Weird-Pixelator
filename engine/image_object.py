import numpy as np


class ImageObject:
    def __init__(self, name, size, pixel_array):
        self.name = name
        self.size = size  # (width, height)
        self.pixel_array = pixel_array  # NumPy array of RGBA values
