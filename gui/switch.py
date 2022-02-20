from .widget import Widget
import pygame.draw


class SwitchGroup(Widget):
    def __init__(self, items=[]):
        #Widget.__init__(self, area)
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.area, 2)


class SwitchItem(Widget):
    def __init__(self, area, color):
        Widget.__init__(self, area)
        self.color = color
        self.cursor = 'hand'

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.area, 2)