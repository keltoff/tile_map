import numpy as np
from itertools import product

from .numeric_layer import NumericLayer


class CellularLayer(NumericLayer):
    def __init__(self, size, name, dtype=float, outside=0.):
        super().__init__(size, name, dtype=dtype, outside=outside)

    def step(self):
        new_data = np.ndarray((self.height, self.width), dtype=self.dtype)
        for y, x in np.ndindex(new_data.shape):
            def get_neighbor(dx=0, dy=0):
                return self.at(x + dx, y + dy)

            new_data[y, x] = self.data[y, x] + self.update_cell(get_neighbor)

        self.data = new_data

    def update_cell(self, get_previous):
        return get_previous()  # copy original value


class DiffusionLayer(CellularLayer):
    def __init__(self, size, name, diffusion_coefficient):
        super().__init__(size, name, dtype=float, outside=0.)

        self.alpha = diffusion_coefficient

    def update_cell(self, get_previous):
        return self.alpha * sum([get_previous(dx=x, dy=y) - get_previous()
                                 for x, y in [[1, 0], [0, 1], [-1, 0], [0, -1]]])
