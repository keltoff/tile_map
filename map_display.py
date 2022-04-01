from .data_types.coords import Pt
from .data_types.position import Position as Pos
from .data_types.direction import Dir
from .geometry import projection
import pygame
from collections import namedtuple
from .gui import Widget


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


class Display:
    def __init__(self, target, projection, map):
        # super().__init__(area=pygame.Rect(target.get_abs_offset(), target.get_size()))
        self.map = map
        self.map.current = 'default'
        self.projection = projection
        self.surface = target
        self.area = pygame.Rect(target.get_abs_offset(), target.get_size())

        self.center_pos = self.map.center()

        self.back_buffer = KeyBuffer(target.get_size())

        self.selected_tile = self.center_pos
        self.zones = []
        self.sprites = []

    def draw(self):
        ptz = [TileRec(t, data, state, pos, self.projection.project(pos)) for pos, t, data, state in self.map.tiles()]

        self.back_buffer.reset()
        # self.surface.lock()

        correction = Pt(self.surface.get_rect().center) - self.projection.project(self.center_pos)

        for tile in sorted(ptz, key=lambda t: t.pt.z, reverse=True):
            self.draw_tile(tile.pt + correction, tile.pos, tile.data)

            for z in self.zones:
                if tile.pos in z:
                    if z.color:
                        self.mark_tile(tile.pt + correction, fill=z.color)

                    if z.border:
                        needs_border =  {direction: tile.pos.shifted(*direction.shift()) not in z for
                                         direction in [Dir.up(), Dir.left(), Dir.down(), Dir.right()] }
                        self.frame_tile(tile.pt + correction, needs_border, z.border)

            if tile.pos.same_place(self.selected_tile):
                self.mark_tile(tile.pt + correction, border=pygame.Color('white'))

            for s in self.sprites:
                if tile.pos.same_place(s.pos):
                    s.pos.z = tile.pos.z  # TODO dat na logictejsi misto
                    s_pt = self.projection.project(s.pos) + correction
                    s.draw(self.surface, s_pt)

        border = self.surface.get_bounding_rect()
        pygame.draw.rect(self.surface, pygame.Color('gray'), border, 2)

        # self.surface.unlock()

    def center(self, position=None):
        if position is None:
            self.center_pos = self.map.center()
        else:
            self.center_pos = position

    def pt_to_pos(self, pt):
        return self.back_buffer.get_pos(Pt(pt) - self.surface.get_abs_offset())

    def draw_tile(self, position: Pt, map_pos: Pos, key):
        pass

    def mark_tile(self, position: Pt, border=None, fill=None):
        pass

    def frame_tile(self, position: Pt, sides, color):
        pass

    def handle(self, event: pygame.event.Event):
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP] and self.area.collidepoint(event.pos):
            pos = self.pt_to_pos(event.pos)
            self.event_pos(pos, event.type, event.button)

    def event_pos(self, pos, event_type, button):
        if button == 1 and event_type == pygame.MOUSEBUTTONDOWN:
            self.selected_tile = pos
        elif button == 3 and event_type == pygame.MOUSEBUTTONDOWN and pos is not None:
            self.center_pos = pos
        else:
            print('Event (b:{}, t:{}) at pos {}'.format(button, event_type, pos))

    def is_passable(self, pos: Pos):
        """Can you walk through the tile? """
        terrain = self.map.map_set.terrain[self.map[pos]]
        return not (terrain.get_b('block_walk') or any(pos.same_place(s.pos) for s in self.sprites))

    def is_clear(self, pos: Pos):
        """ Is the tile clear for LoS effect? """
        terrain = self.map.map_set.terrain[self.map[pos]]
        return not (terrain.get_b('block_shoot') or any(pos.same_place(s.pos) for s in self.sprites))


class OrthoSketch(Display):
    def __init__(self, target, map, tile_size=10):
        proj = projection.Ortho(scale=tile_size)
        Display.__init__(self, target, projection=proj, map=map)

        self.tile_size = tile_size

    def draw_tile(self, position: Pt, pos: Pos, data):
        color = data['color']  # pygame.Color('cyan')
        rect = pygame.Rect(position.x, position.y, 1, 1).inflate(self.tile_size - 3, self.tile_size - 3)
        pygame.draw.rect(self.surface, color, rect, 3)
        self.back_buffer.mark_rect(rect, pos)

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


class IsoSketch(Display):
    def __init__(self, target, map, tile_size=10, tilt=45):
        proj = projection.Iso(scale=tile_size, tilt=tilt)
        Display.__init__(self, target, projection=proj, map=map)

        self.tile_w = int(proj.x_step)
        self.tile_h = int(proj.y_step)
        self.tile_d = int(proj.z_step)

    def draw_tile(self, position: Pt, pos: Pos, data):
        color = data['color']  # pygame.Color('cyan')

        points = [position - Pt(self.tile_w, 0),
                  position - Pt(0, self.tile_h),
                  position + Pt(self.tile_w, 0),
                  position + Pt(0, self.tile_h)]

        bordered_polygon(self.surface, color, points)
        self.back_buffer.mark_poly(points, pos)

        for i in range(int(data['height'])):
            base = position + Pt(0, self.tile_d * i)
            l_points = [base + Pt(-self.tile_w, 0),
                        base + Pt(0, self.tile_h),
                        base + Pt(0, self.tile_h + self.tile_d),
                        base + Pt(-self.tile_w, self.tile_d)]
            r_points = [base + Pt(self.tile_w, 0),
                        base + Pt(0, self.tile_h),
                        base + Pt(0, self.tile_h + self.tile_d),
                        base + Pt(self.tile_w, self.tile_d)]
            bordered_polygon(self.surface, color, l_points)
            self.back_buffer.mark_poly(l_points, pos)
            bordered_polygon(self.surface, color, r_points)
            self.back_buffer.mark_poly(r_points, pos)

    def mark_tile(self, position: Pt, border=None, fill=None):
        points = [position - Pt(self.tile_w - 7, 0),
                  position - Pt(0, self.tile_h - 4),
                  position + Pt(self.tile_w - 7, 0),
                  position + Pt(0, self.tile_h - 4)]

        if border:
            pygame.draw.polygon(self.surface, border, points, 1)

        if fill:
            pygame.draw.polygon(self.surface, fill, points, 0)

    def frame_tile(self, position: Pt, sides, color):
        points = [position - Pt(self.tile_w - 5, 0),
                  position - Pt(0, self.tile_h - 3),
                  position + Pt(self.tile_w - 5, 0),
                  position + Pt(0, self.tile_h - 3)]
        for i, direction in enumerate([Dir.left(), Dir.up(), Dir.right(), Dir.down()]):
            if sides[direction]:
                pygame.draw.line(self.surface, color, points[i], points[(i+1) % 4], width=2)


def bordered_polygon(surface, color, points, width=2):
    pygame.draw.polygon(surface, pygame.Color('black'), points, 0)
    pygame.draw.polygon(surface, color, points, width)
