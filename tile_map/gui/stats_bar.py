from .widget import Widget
import pygame.draw
from pygame import Color, Rect
import text_helper
import stats_helper


class StatsBar(Widget):
    def __init__(self, area, sprites):
        Widget.__init__(self, area)
        self.sprites = sprites
        self.items = []
        self.color = (50, 50, 50)

        self.margin = 5
        self.tab = 40

        self.debug = False

    def draw(self, surface):
        canvas = surface.subsurface(self.area)
        pygame.draw.rect(canvas, self.color, canvas.get_rect(), 2)

        for item in self.items:
            item.draw(canvas)

    def display(self, data):
        self.items = []
        if _has_any_(data, 'terrain'):
            self.add_item(TerrainBarItem, data['terrain'])

        self.add_section(data, 'places', PlaceBarItem, 'Places')
        self.add_section(data, 'heroes', HeroBarItem, 'Heroes')
        self.add_section(data, 'monsters', MonsterBarItem, 'Monsters')

    def add_section(self, data, key, item_class, section_name):
        if _has_any_(data, key):
            self.add_item(TextBarItem, section_name)
            for x in data[key]:
                self.add_item(item_class, x)

    def add_item(self, item_class, item_data):
        taken = sum((i.height + self.margin for i in self.items))
        item_area = Rect(self.margin, taken + self.margin, self.area.width-2*self.margin, 0)
        self.items.append(item_class(item_area, self, item_data))


class BarItem(Widget):
    def __init__(self, area, bar):
        Widget.__init__(self, area)
        self.area.height = 30
        self.bar = bar

    def draw(self, surface):
        if self.bar.debug:
            pygame.draw.rect(surface, Color('cyan'), self.area, 1)

    def get_cursor(self, pos):
        return self.bar.get_cursor(pos)

    @property
    def height(self):
        return self.area.height


class TerrainBarItem(BarItem):
    def __init__(self, area, bar, terrain):
        BarItem.__init__(self, area, bar)
        self.terrain = terrain
        self.area.height = 65

    def draw(self, surface):
        BarItem.draw(self, surface)
        canvas = surface.subsurface(self.area)
        self.bar.sprites.blit(canvas, (20, 20), self.terrain['sprite'])
        text_helper.draw_text(canvas, self.terrain['name'], (self.bar.tab, 12), Color('gray'))
        stats_helper.draw(canvas, (self.bar.tab, 40), self.terrain.get_n('food'), 'green')
        stats_helper.draw(canvas, (self.bar.tab, 55), self.terrain.get_n('material'), 'blue')


class MonsterBarItem(BarItem):
    def __init__(self, area, bar, monster):
        BarItem.__init__(self, area, bar)
        self.monster = monster

    def draw(self, surface):
        BarItem.draw(self, surface)
        canvas = surface.subsurface(self.area)
        self.bar.sprites.blit(canvas, (16, 16), self.monster.type)
        text_helper.draw_text(canvas, self.monster.type, (self.bar.tab, 7), Color('gray'))


class PlaceBarItem(BarItem):
    def __init__(self, area, bar, place):
        BarItem.__init__(self, area, bar)
        self.place = place

    def draw(self, surface):
        BarItem.draw(self, surface)
        canvas = surface.subsurface(self.area)
        self.bar.sprites.blit(canvas, (16, 16), self.place.key)
        text_helper.draw_text(canvas, self.place.key, (self.bar.tab, 7), Color('gray'))


class TextBarItem(BarItem):
    def __init__(self, area, bar, text):
        BarItem.__init__(self, area, bar)
        self.text = text

    def draw(self, surface):
        BarItem.draw(self, surface)
        canvas = surface.subsurface(self.area)
        text_helper.draw_text(canvas, self.text, (7, 14), Color('gray'))


class HeroBarItem(BarItem):
    def __init__(self, area, bar, hero):
        BarItem.__init__(self, area, bar)
        self.hero = hero

    def draw(self, surface):
        BarItem.draw(self, surface)
        canvas = surface.subsurface(self.area)
        self.bar.sprites.blit(canvas, (16, 16), self.hero.sprite)
        text_helper.draw_text(canvas, self.hero.character_class, (self.bar.tab, 7), Color('gray'))


def _has_any_(dictionary, key):
    return key in dictionary and dictionary[key]
