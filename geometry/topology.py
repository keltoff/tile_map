from ..data_types.position import Position
from ..data_types.direction import Dir
from ..data_types.zone import Zone, LambdaZone


class Topology:
    def __init__(self):
        pass
    
    @classmethod
    def directions(cls):
        raise NotImplemented()

    @classmethod
    def neighbors(cls, pos: Position):
        return [pos.shifted(*d) for d in cls.directions()]

    @classmethod
    def distance(cls, pos1: Position, pos2: Position):
        pass

    @classmethod
    def find_path(cls, pos1: Position, pos2: Position, passable=lambda pos: True):
        open = [pos1]
        closed = []
        prev = dict()

        if not (pos2 and passable(pos2)):
            return None

        while open:
            node = open.pop(0)
            for n in cls.neighbors(node):
                if pos2.same_place(n):
                    # target found
                    path = [pos2]
                    cursor = node
                    while cursor != pos1:
                        # path.append(cursor)
                        path_segment = cursor.but(dir=cls.dir_from(cursor, prev[cursor]))
                        path.append(path_segment)

                        cursor = prev[cursor]
                    return list(reversed(path))

                if n.place not in closed:
                    if passable(n):
                        open.append(n)
                        prev[n] = node
                    else:
                        closed.append(n.place)

            closed.append(node.place)
            open = sorted(open, key=lambda a: cls.distance(a, pos2))

        return None

    @classmethod
    def trace_shot(cls, origin: Position, target: Position):
        shift_prime, steps_prime, shift_sec, steps_sec = cls.decompose_shifts(origin, target)

        acc = 0.5
        slope_h = steps_sec / steps_prime
        height = origin.z
        slope_z = (target.z - origin.z) / (steps_prime + steps_sec)

        shot = []

        pos = origin
        for p in range(steps_prime):
            pos = pos.shifted(*shift_prime)

            height += slope_z
            pos.z = int(round(height))

            shot.append(pos)

            acc += slope_h

            if acc > 1.0:
                acc -= 1.0
                pos = pos.shifted(*shift_sec)
                height += slope_z
                pos.z = int(round(height))
                shot.append(pos)

        return shot

    @classmethod
    def dir_to(cls, pos: Position, target: Position):
        raise NotImplemented()

    @classmethod
    def decompose_shifts(cls, origin: Position, target: Position):
        raise NotImplemented()

    @classmethod
    def dir_from(cls, pos: Position, target: Position):
        return cls.dir_to(target, pos)

    @classmethod
    def zone_near(cls, pos: Position, size):
        # near = {pos: 0}
        #
        # for step in range(size):
        #     for p in list(near.keys()):
        #         for np in cls.neighbors(p):
        #             old_val = near.get(np, 9999)
        #             new_val = near[p] + 1
        #             if old_val > new_val:
        #                 near[np] = new_val
        #     near = near
        #
        # return Zone(list(near.keys()))
        return LambdaZone(lambda q: cls.distance(pos, q) <= size)

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
    def directions(cls):
        return [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    @classmethod
    def distance(cls, pos1, pos2):
        #return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

        # using distance from Flat8 so pathfinding doesn't look THAT weird
        adx, ady = map(abs, _dxy_(pos1, pos2))
        if adx > ady:
            return adx + 0.4 * ady
        else:
            return ady + 0.4 * adx

    @classmethod
    def dir_to(cls, pos: Position, target: Position):
        dx, dy = _dxy_(pos, target)
        if abs(dx) > abs(dy):
            if dx > 0:
                return Dir(1)
            else:
                return Dir(3)
        else:
            if dy > 0:
                return Dir(2)
            else:
                return Dir(0)

    @classmethod
    def decompose_shifts(cls, origin: Position, target: Position):
        dx, dy = target.x - origin.x, target.y - origin.y
        adx, ady = abs(dx), abs(dy)
        steps_prime, steps_sec = max(adx, ady), min(adx, ady)

        if adx > ady:
            shift_prime = int(dx / adx), 0
        else:
            shift_prime = 0, int(dy / ady)

        if steps_sec == 0:
            shift_sec = 0, 0
        else:
            if adx > ady:
                shift_sec = 0, int(dy / ady)
            else:
                shift_sec = int(dx / adx), 0

        return shift_prime, steps_prime, shift_sec, steps_sec


class Flat8(Topology):
    @classmethod
    def directions(cls):
        return [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    
    @classmethod
    def distance(cls, pos1, pos2):
        #return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
        dx = abs(pos1.x - pos2.x)
        dy = abs(pos1.y - pos2.y)
        if dx > dy:
            return dx + 0.4 * dy
        else:
            return dy + 0.4 * dx


class Hexa(Topology):
    @classmethod
    def directions(cls):
        return [(0, 1), (1, 1), (1, 0), (0, -1), (-1, -1), (-1, 0)]

    @classmethod
    def distance(cls, pos1, pos2):
        return sum(cls.decompose_shifts(pos1, pos2))

    @classmethod
    def dir_to(cls, pos: Position, target: Position):
        shifts = list(cls.decompose_shifts(pos, target).values())
        idx = shifts.index(max(shifts))
        return Dir(idx)  # TODO we need Dir6

    @classmethod
    def decompose_shifts(cls, origin: Position, target: Position):
        dx, dy = _dxy_(origin, target)

        factors = {d: _divide((dx, dy), d) for d in cls.directions()}
        for d in cls.directions():
            for d2 in cls.directions():
                if d != d2 and _divide(d2, d) > 0:
                    factors[d2] -= factors[d]

        return factors
        # return shift_prime, steps_prime, shift_sec, steps_sec


def _dxy_(pos1: Position, pos2: Position):
    dx = pos2.x - pos1.x
    dy = pos2.y - pos1.y
    return dx, dy


def _divide(xy, divxy):
    x, y = xy
    dx, dy = divxy
    if x * dx <= 0 or y * dy <= 0:
        return 0
    else:
        return min(x // dx, y // dy)
