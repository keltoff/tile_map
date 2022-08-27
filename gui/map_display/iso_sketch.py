from tile_map.data_types.coords import Pt
from tile_map.data_types.position import Position as Pos
from tile_map.data_types.direction import Dir
from tile_map.geometry import projection
from .map_display_base import BaseMapDisplay
import pygame


class IsoSketch(BaseMapDisplay):
    def __init__(self, target, map, tile_size=10, tilt=45):
        proj = projection.Iso(scale=tile_size, tilt=tilt)
        BaseMapDisplay.__init__(self, target, projection=proj, map=map)

        self.tile_w = int(proj.x_step)
        self.tile_h = int(proj.y_step)
        self.tile_d = int(proj.z_step)

    def _tile_corners(self, position: Pt, margin_h=0, margin_w=0):
        return [position - Pt(self.tile_w - margin_w, 0),
                position - Pt(0, self.tile_h - margin_h),
                position + Pt(self.tile_w - margin_w, 0),
                position + Pt(0, self.tile_h - margin_h)]

    def _draw_tile_area(self, tile, correction):
        super()._draw_tile_area(tile, correction)

        self.back_buffer.mark_poly(self._tile_corners(tile.pt + correction), tile.pos)

    def draw_tile(self, position: Pt, pos: Pos, data):
        color = data['color']  # pygame.Color('cyan')

        bordered_polygon(self.surface, color, self._tile_corners(position))

        for i in range(int(data['height'])):
            base = position + Pt(0, self.tile_d * i)

            cr = self._tile_corners(base)
            d_step = (0, self.tile_d)
            l_points = [cr[0], cr[3], cr[3] + d_step, cr[0] + d_step]
            r_points = [cr[2], cr[3], cr[3] + d_step, cr[2] + d_step]

            bordered_polygon(self.surface, color, l_points)
            bordered_polygon(self.surface, color, r_points)
            self.back_buffer.mark_poly(l_points, pos)
            self.back_buffer.mark_poly(r_points, pos)

    def mark_tile(self, position: Pt, border=None, fill=None):
        points = self._tile_corners(position, margin_w=7, margin_h=4)

        if border:
            pygame.draw.polygon(self.surface, border, points, 1)

        if fill:
            pygame.draw.polygon(self.surface, fill, points, 0)

    def frame_tile(self, position: Pt, sides, color):
        points = self._tile_corners(position, margin_w=5, margin_h=3)
        for i, direction in enumerate([Dir.left(), Dir.up(), Dir.right(), Dir.down()]):
            if sides[direction]:
                pygame.draw.line(self.surface, color, points[i], points[(i+1) % 4], width=2)


def bordered_polygon(surface, color, points, width=2):
    pygame.draw.polygon(surface, pygame.Color('black'), points, 0)
    pygame.draw.polygon(surface, color, points, width)
