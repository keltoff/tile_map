from ..data_types.position import Position
from ..data_types.zone import Zone


class Topology:
    def __init__(self):
        pass

    @classmethod
    def neighbors(cls, pos: Position):
        return []

    @classmethod
    def distance(cls, pos1: Position, pos2: Position):
        pass

    @classmethod
    def find_path(cls, pos1: Position, pos2: Position):
        pass

    @classmethod
    def zone_near(cls, pos: Position, size):
        near = {pos: 0}

        for step in range(size):
            for p in list(near.keys()):
                for np in cls.neighbors(p):
                    old_val = near.get(np, 9999)
                    new_val = near[p] + 1
                    if old_val > new_val:
                        near[np] = new_val
            near = near

        return Zone(list(near.keys()))

    @classmethod
    def zone_beam(cls, pos: Position, length):
        x = pos
        positions = []
        for i in range(length):
            x = x.fwd()
            positions.append(x)
        return Zone(positions)


class Flat4(Topology):
    @classmethod
    def neighbors(cls, pos: Position):
        return [pos.shifted(0, 1), pos.shifted(1, 0), pos.shifted(0, -1), pos.shifted(-1, 0)]

    @classmethod
    def distance(cls, pos1, pos2):
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


class Flat8(Topology):
    @classmethod
    def neighbors(cls, pos: Position):
        return [pos.shifted(0, 1), pos.shifted(1, 1), pos.shifted(1, 0), pos.shifted(1, -1),
                pos.shifted(0, -1), pos.shifted(-1, -1), pos.shifted(-1, 0), pos.shifted(-1, 1)]
