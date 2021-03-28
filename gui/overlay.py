import math
import pygame.draw


class Overlay:
    def __init__(self):
        self.selector = lambda pos, terrain: False

    def draw(self, surface, pos):
        pass

    def relevant(self, pos, terrain):
        return self.selector(pos, terrain)


class ColorOverlay(Overlay):
    def __init__(self, color):
        Overlay.__init__(self)
        self.color = color

        self.shade = pygame.Surface((100, 100))  # the size of your rect
        self.shade.set_alpha(self.color.a)                # alpha level
        self.shade.fill(self.color)           # this fills the entire surface

    def draw(self, surface, pos):
        surface.blit(self.shade, (0, 0))    # (0,0) are the top-left coordinates


class HeroOverlay(ColorOverlay):
    def __init__(self, hero):
        ColorOverlay.__init__(self, pygame.Color(0, 250, 100, 150))
        self.selector = dist_L2(hero.pos, hero.range)


class MonsterOverlay(ColorOverlay):
    def __init__(self, monster):
        ColorOverlay.__init__(self, pygame.Color(250, 50, 0, 150))
        self.selector = dist_L2(monster.pos, monster.range)


def dist_L1(target, maximum):
    def selector(x, _):
        d = x - target
        return abs(d[0]) + abs(d[1]) <= maximum
    return selector


def dist_L2(target, maximum):
    def selector(x, _):
        d = x - target
        return math.sqrt(d[0]*d[0] + d[1]*d[1]) <= maximum
    return selector
