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


class IsoFixed(Projection):
    def __init__(self, x_step, y_step, z_step, center=(0, 0)):
        self.center = center
        self.x_step = x_step
        self.y_step = y_step
        self.z_step = z_step

    def project(self, pos: Pos):
        x = self.x_step * (pos.x - pos.y)
        y = self.y_step * (pos.x + pos.y)
        h = self.z_step * pos.z
        depth = -y
        return Pt(x, y-h, z=depth, dir=pos.dir)


class Iso(IsoFixed):
    def __init__(self, center=(0, 0), scale=20.0, tilt=0.45):

        self.scale = scale
        self.tilt_r = math.radians(tilt)

        super().__init__(x_step=scale, y_step=scale * math.cos(self.tilt_r), z_step=scale * math.sin(self.tilt_r), center=center)


class HexaOrthoH(Projection):
    """
    Orthographic projection on the hex grid.
    Horizontal variant - Pos.x axis is equal to x axis on monitor
    """
    def __init__(self, scale=20.0):
        w = math.sqrt(3) * scale
        h = 2 * scale

        self.x_step = w
        self.y_step = h * 3/4

    def project(self, pos: Pos):
        x = self.x_step * (pos.x - 0.5 * pos.y)
        y = self.y_step * pos.y
        return Pt(x, y, z=-y, dir=pos.dir)


class HexaOrthoV(Projection):
    """
    Orthographic projection on the hex grid.
    Vertical variant - Pos.y axis is equal to y axis on monitor
    """
    def __init__(self, scale=20.0):
        self.w = 2 * scale
        self.h = math.sqrt(3) * scale

        self.x_step = self.w * 3/4
        self.y_step = self.h

    def project(self, pos: Pos):
        x = self.x_step * pos.x
        y = self.y_step * (pos.y - 0.5 * pos.x)
        return Pt(x, y, z=-y, dir=pos.dir)
