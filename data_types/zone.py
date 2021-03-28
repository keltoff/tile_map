import pygame


class Zone:
    def __init__(self, positions=[], color=pygame.Color('green')):
        self.positions = positions
        self.color = color

    def __contains__(self, item):
        return any(p.same_place(item) for p in self.positions)

    def __iter__(self):
        return self.positions.__iter__()

    def paint(self, color):
        return Zone(self.positions.copy(), pygame.Color(color))
