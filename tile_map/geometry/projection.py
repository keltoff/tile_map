from ..data_types.position import Position as Pos
from ..data_types.coords_ex import Pt
import math


class Projection:
    def project(self, pos: Pos) -> (Pt, float):
        pass

    def __call__(self, *args, **kwargs):
        return self.project(*args, **kwargs)

    def reverse(self, pt: Pt) -> Pos:
        pass


class Ortho(Projection):
    def __init__(self, center=(0, 0), scale=20.0):
        self.center = center
        self.scale = scale

    def project(self, pos: Pos):
        return Pt(pos.x * self.scale, pos.y * self.scale, z=0, dir=pos.dir) - self.center

    def reverse(self, pt: Pt):
        p0 = pt + self.center
        return Pos(int(p0.x / self.scale), int(p0.y / self.scale))


class Iso(Projection):
    def __init__(self, center=(0, 0), scale=20.0, tilt=0.45):
        self.center = center
        self.scale = scale
        self.tilt = math.radians(tilt)

    def project(self, pos: Pos):
        x = self.scale * (pos.x - pos.y)
        y = self.scale * (pos.x + pos.y) * self.y_skew
        h = self.scale * pos.z * self.z_skew
        depth = -y
        return Pt(x, y-h, z=depth, dir=pos.dir)

    @property
    def y_skew(self):
        return math.cos(self.tilt)

    @property
    def z_skew(self):
        return math.sin(self.tilt)

