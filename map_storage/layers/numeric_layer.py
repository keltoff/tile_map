import numpy as np

from .base_layer import BaseLayer


class NumericLayer(BaseLayer):
    def __init__(self, size, name, dtype=float, outside=0.):
        super().__init__(size, name)

        self.dtype = dtype
        self.data = np.zeros((self.height, self.width), dtype=dtype)
        self.outside = dtype(outside)

    def at(self, x, y):
        if self.is_inside(x, y):
            return self.data[y, x]
        else:
            return self.outside

    @property
    def max(self):
        return self.data.max

    @property
    def min(self):
        return self.data.min
