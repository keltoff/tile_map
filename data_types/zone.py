import pygame


class Zone:
    def __init__(self, positions=[], color=None, border=None):
        self.positions = positions
        self.color = color
        self.border = border

    def __contains__(self, item):
        return any(p.same_place(item) for p in self.positions)

    def __iter__(self):
        return self.positions.__iter__()

    def paint(self, color=None, border=None):
        if color is None:
            color = self.color
        else:
            color = pygame.Color(color)

        if border is None:
            border = self.border
        else:
            border = pygame.Color(border)

        return Zone(self.positions.copy(), color=color, border=border)


class LambdaZone:
    def __init__(self, selector, color=None, border=None):
        self.selector = selector
        self.color = color
        self.border = border

    def __contains__(self, item):
        return self.selector(item)

    def paint(self, color=None, border=None):
        if color is None:
            color = self.color

        if border is None:
            border = self.border

        return self.__class__(self.selector, color=pygame.Color(color), border=pygame.Color(border))

