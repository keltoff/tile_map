from tile_map.data_types.coords import Pt
from tile_map.data_types.position import Position as Pos
from tile_map.data_types.direction import Dir
from tile_map.geometry import projection
from .map_display_base import BaseMapDisplay
import pygame


class OrthoSketch(BaseMapDisplay):
    def __init__(self, target, map, tile_size=10):
        proj = projection.Ortho(scale=tile_size)
        BaseMapDisplay.__init__(self, target, projection=proj, map=map)

        self.tile_size = tile_size

    def _draw_tile_area(self, tile, correction):
        super()._draw_tile_area(tile, correction)
        self.back_buffer.mark_rect(self._tile_rect(tile.pt + correction, margin=1), tile.pos)

    def _tile_rect(self, center: Pt, margin=1):
        return pygame.Rect(center.x, center.y, 1, 1).inflate(self.tile_size - margin, self.tile_size - margin)

    def draw_tile(self, position: Pt, pos: Pos, data):
        color = data['color']  # pygame.Color('cyan')
        rect = self._tile_rect(position, margin=3)
        pygame.draw.rect(self.surface, color, rect, 3)

    def mark_tile(self, position: Pt, border=None, fill=None):
        rect = pygame.Rect(position.x, position.y, 0, 0).inflate(self.tile_size - 7, self.tile_size - 7)

        if border:
            pygame.draw.rect(self.surface, border, rect, 1)

        if fill:
            pygame.draw.rect(self.surface, fill, rect, 0)

    def frame_tile(self, position: Pt, sides, color):
        side = self.tile_size/2 - 2
        points = [position + Pt(-side, side),
                  position + Pt(-side, -side),
                  position + Pt(side, -side),
                  position + Pt(side, side)]
        for i, direction in enumerate([Dir.left(), Dir.up(), Dir.right(), Dir.down()]):
            if sides[direction]:
                pygame.draw.line(self.surface, color, points[i], points[(i+1) % 4], width=2)
