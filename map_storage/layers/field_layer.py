import numpy as np

from .numeric_layer import NumericLayer


class FieldLayer(NumericLayer):
    def __init__(self, size, name):
        super().__init__(size, name, dtype=int, outside=0)

        self.cores = []

    def recompute(self, cores=None):
        if cores:
            self.cores = cores

        self.data = np.zeros((self.height, self.width), dtype=int)

        for core in self.cores:
            self.data[_field_area_(core)] += 1

    def move(self, core, move_to):
        if core in self.cores:
            self.data[_field_area_(core)] -= 1
        else:
            self.cores.append(core)

        core.pos = move_to
        self.data[_field_area_(core)] += 1


def _field_area_(core):
    x, y = core.pos.x, core.pos.y
    r = core.range
    return slice(y-r, y+r+1), slice(x-r, x+r+1)
