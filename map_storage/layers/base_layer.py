from __future__ import annotations
from tile_map.data_types.position import Position
from functools import singledispatchmethod


class BaseLayer:
    def __init__(self, size, name):
        self.width, self.height = size
        self.name = name

    @singledispatchmethod
    def __getitem__(self, item):
        raise KeyError('Unsupported address type')

    @__getitem__.register
    def _(self, item: tuple):
        x, y = item
        return self.at(x, y)

    @__getitem__.register
    def _(self, item: Position):
        return self.at(item.x, item.y)

    def at(self, x, y):
        return None

    def is_inside(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    @classmethod
    def match_to(cls, data_layer: BaseLayer, suffix='_2'):
        return cls(size=(data_layer.width, data_layer.height),
                   name=data_layer.name + suffix)
