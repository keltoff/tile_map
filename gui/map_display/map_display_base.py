from collections import namedtuple

import pygame

from tile_map.data_types.coords import Pt
from tile_map.data_types.direction import Dir
from tile_map.data_types.position import Position as Pos
from tile_map.geometry.projection import Projection

TileRec = namedtuple('TileRec', 'terrain data state pos pt')


class KeyBuffer:
    def __init__(self, size):
        self.buffer = pygame.Surface(size, flags=0, depth=32)
        self.k2c = dict()
        self.c2k = dict()

    def mark_poly(self, points, key):
        color = self._key2color_(key)
        pygame.draw.polygon(self.buffer, color, points, 0)

    def mark_rect(self, rect, key):
        color = self._key2color_(key)
        pygame.draw.rect(self.buffer, color, rect, 0)

    def get_pos(self, pt: Pt):
        color = int(self.buffer.get_at(pt))
        return self.c2k.get(color, None)

    def reset(self):
        self.buffer.fill(pygame.Color(0, 0, 0))
        self.c2k.clear()
        self.k2c.clear()

    def _key2color_(self, key):
        if key in self.k2c:
            return pygame.Color(self.k2c[key])
        else:
            new_idx = len(self.k2c) + 1
            new_color = 256 * new_idx + 255
            self.k2c[key] = new_color
            self.c2k[new_color] = key
            return pygame.Color(new_color)


class BaseMapDisplay:
    def __init__(self, target: pygame.Surface, projection: Projection, map):
        # super().__init__(area=pygame.Rect(target.get_abs_offset(), target.get_size()))
        self.map = map
        self.map.current = 'default'
        self.projection = projection
        self.surface = target
        self.area = pygame.Rect(target.get_abs_offset(), target.get_size())

        self.center_pos = self.map.center()

        self.back_buffer = KeyBuffer(target.get_size())

    def draw(self):
        ptz = [TileRec(t, data, state, pos, self.projection.project(pos)) for pos, t, data, state in self.map.tiles()]

        self.back_buffer.reset()
        # self.surface.lock()

        correction = Pt(self.surface.get_rect().center) - self.projection.project(self.center_pos)

        for tile in sorted(ptz, key=lambda t: t.pt.z, reverse=True):
            self._draw_tile_area(tile, correction)

        border = self.surface.get_bounding_rect()
        pygame.draw.rect(self.surface, pygame.Color('gray'), border, 2)

        # self.surface.unlock()

    def _draw_tile_area(self, tile, correction):
        self.draw_tile(tile.pt + correction, tile.pos, tile.data)

    def center(self, position=None):
        if position is None:
            self.center_pos = self.map.center()
        else:
            self.center_pos = position

    def pt_to_pos(self, pt):
        return self.back_buffer.get_pos(Pt(pt) - self.surface.get_abs_offset())

    # DESCENDANT NEEDS TO IMPLEMENT:
    # def draw_tile(self, position: Pt, map_pos: Pos, key):
    #     pass

    def handle(self, event: pygame.event.Event):
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP] and self.area.collidepoint(event.pos):
            pos = self.pt_to_pos(event.pos)
            self.event_pos(pos, event.type, event.button)

    def event_pos(self, pos, event_type, button):
        pass


class MapDisplayZones(BaseMapDisplay):
    def __init__(self, *params):
        super().__init__(*params)

        self.zones = []

    def _draw_tile_area(self, tile, correction):
        super()._draw_tile_area(tile, correction)

        for z in self.zones:
            if tile.pos in z:
                if z.color:
                    self.mark_tile(tile.pt + correction, fill=z.color)

                if z.border:
                    needs_border = {direction: tile.pos.shifted(*direction.shift()) not in z for
                                    direction in [Dir.up(), Dir.left(), Dir.down(), Dir.right()]}
                    self.frame_tile(tile.pt + correction, needs_border, z.border)

    # DESCENDANT NEEDS TO IMPLEMENT:
    # def mark_tile(self, position: Pt, border=None, fill=None):
    #     pass
    #
    # def frame_tile(self, position: Pt, sides, color):
    #     pass


class MapDisplaySelection(BaseMapDisplay):
    def __init__(self, *params):
        super().__init__(*params)
        self.selected_tile = self.center_pos

        # self.mark_tile = lambda *args, **kwargs: None

    def _draw_tile_area(self, tile, correction):
        super()._draw_tile_area(tile, correction)

        if tile.pos.same_place(self.selected_tile):
            self.mark_tile(tile.pt + correction, border=pygame.Color('white'))

    # DESCENDANT NEEDS TO IMPLEMENT:
    # def mark_tile(self, position: Pt, border=None, fill=None):
    #     pass


class MapDisplaySprites(BaseMapDisplay):
    def __init__(self, *params):
        super().__init__(*params)
        self.sprites = []

    def _draw_tile_area(self, tile, correction):
        super()._draw_tile_area(tile, correction)

        for s in self.sprites:
            if tile.pos.same_place(s.pos):
                s.pos.z = tile.pos.z  # TODO dat na logictejsi misto
                s_pt = self.projection.project(s.pos) + correction
                s.draw(self.surface, s_pt)

    def is_passable(self, pos: Pos):
        """Can you walk through the tile? """
        terrain = self.map.map_set.terrain[self.map[pos]]
        return not (terrain.get_b('block_walk') or any(pos.same_place(s.pos) for s in self.sprites))

    def is_clear(self, pos: Pos):
        """ Is the tile clear for LoS effect? """
        terrain = self.map.map_set.terrain[self.map[pos]]
        return not (terrain.get_b('block_shoot') or any(pos.same_place(s.pos) for s in self.sprites))


class ExampleDisplay(MapDisplayZones, MapDisplaySelection, MapDisplaySprites):
    def event_pos(self, pos, event_type, button):
        if button == 1 and event_type == pygame.MOUSEBUTTONDOWN:
            self.selected_tile = pos
        elif button == 3 and event_type == pygame.MOUSEBUTTONDOWN and pos is not None:
            self.center_pos = pos
        else:
            print('Event (b:{}, t:{}) at pos {}'.format(button, event_type, pos))