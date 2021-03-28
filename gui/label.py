from .widget import Widget
import pygame.draw
import pygame.font
from pygame import Rect

textfont = pygame.font.SysFont('default', 20)


class Label(Widget):
    def __init__(self, pos, text, color):
        self.buffer = textfont.render(text, True, color)
        Widget.__init__(self, Rect(pos, self.buffer.get_size()))
        self.text = text
        self.color = color

    def draw(self, surface):
        surface.blit(self.buffer, self.area.topleft)
