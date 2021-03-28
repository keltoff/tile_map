import pygame
import pygame.font
import pygame.locals as pl

from auxiliary import Pt, SafeDict
from widget import Widget

import map_data
import overlay


class Map(Widget):
    def __init__(self, area):
        Widget.__init__(self, area)
        self.data = map_data.MapData()
        self.tile_size = 32
        self.origin = Pt(0, 0)
        self.frame_color = (255, 200, 150)
        self.selected_tile = None
        self.selected_hero = None
        self.scroll_speed = Pt(0, 0)
        self.keydir = __build_keydir__()

        self.sprites = None
        self.font = pygame.font.SysFont('default', 50)

        self.overlay = dict()

    def load(self, filename):
        self.data.load(filename)

    def draw(self, surface):
        surface.fill((0, 0, 0), self.area)
        self.draw_map(surface.subsurface(self.area))
        pygame.draw.rect(surface, self.frame_color, self.area, 2)

    def draw_map(self, surface):
        tile = pygame.Rect(0, 0, self.tile_size, self.tile_size)

        def current_view(xy):
            return xy * self.tile_size - self.origin

        if self.data:
            for x, y, ter in self.data:
                target = tile.move(current_view(Pt(x, y)))
                if target.width > 0:
                    # pygame.draw.rect(surface, ter['color'], target)
                    subkey = self.data.neighborhood(x, y, ter)
                    self.sprites.blit(surface, target, ter['sprite'], subkey)

                    for o in self.overlay.values():
                        if o.relevant(Pt(x, y), ter):
                            o.draw(surface.subsurface(target), Pt(x, y))

        for c in self.data.places:
            self.sprites.blit(surface, tile.move(current_view(c.pos)), c.key)

        for m in self.data.monsters:
            self.sprites.blit(surface, tile.move(current_view(m.pos)), m.type)

        for h in self.data.heroes:
            self.sprites.blit(surface, tile.move(current_view(h.pos)), h.sprite)

        if self.selected_tile:
            # draw_text(surface, '{}'.format(self.selected_tile), self.area.topleft, (0, 200, 0))
            pygame.draw.rect(surface, pygame.Color('red'), tile.move(current_view(self.selected_tile)), 2)

    def update(self):
        self.origin += self.scroll_speed * 3

        if self.origin.x < 0:
            self.origin = Pt(0, self.origin.y)

        if self.origin.y < 0:
            self.origin = Pt(self.origin.x, 0)

    def get_cursor(self, pos):
        tile = self.tile_at(pos)
        if self.selected_hero and self.data.stuff_at(self.data.monsters, tile):
            return 'strike'
        elif self.tile_at(pos):
            return 'frame'
        else:
            return None

    def tile_at(self, pos):
        tile_pos = (pos + self.origin) / self.tile_size
        if self.data[tile_pos]:
            return tile_pos
        else:
            return None

    def tile_selected(self, stuff):
        pass

    # event handling
    def process_event(self, event):
        if event.type == pl.KEYDOWN:
            # fast = event.mod
            self.scroll_speed += self.keydir[event.key]
        if event.type == pl.KEYUP:
            self.scroll_speed -= self.keydir[event.key]

    def click(self, pos, button):
        tile = self.tile_at(pos)
        if button == 1:
            self.select_tile(tile)
        if button == 3 and self.selected_hero:
            mon = self.data.stuff_at(self.data.monsters, tile)
            if mon:
                self.start_fight(self.selected_hero, mon[0])

                pass
            else:
                self.selected_hero.pos = tile
                self.select_tile(tile)

    def select_tile(self, tile):
        self.selected_tile = tile

        heroes = self.data.stuff_at(self.data.heroes, tile)
        monsters = self.data.stuff_at(self.data.monsters, tile)

        if monsters:
            self.overlay['range'] = overlay.MonsterOverlay(monsters[0])
            self.selected_hero = None
        elif heroes:
            self.selected_hero = heroes[0]
            self.overlay['range'] = overlay.HeroOverlay(heroes[0])
        else:
            self.overlay.pop('range', None)
            self.selected_hero = None

        self.tile_selected({'terrain': self.data.terrain_at(tile),
                            'places': self.data.stuff_at(self.data.places, tile),
                            'monsters': monsters,
                            'heroes': heroes})

    def start_fight(self, hero, monster):
        pass

    def mouse_move(self, pos):
        pass


def __build_keydir__():
    keydir = SafeDict()
    keydir[pl.K_UP] = Pt(0, -1)
    keydir[pl.K_DOWN] = Pt(0, 1)
    keydir[pl.K_LEFT] = Pt(-1, 0)
    keydir[pl.K_RIGHT] = Pt(1, 0)
    keydir.default = Pt(0, 0)
    return keydir
