import pygame.locals as pl

from ..data_types.coords_ex import Pt


class Gui:
    def __init__(self):
        self.parts = []

    def draw(self, surface):
        for part in self.parts:
            part.draw(surface)

    def handle(self, event):

        if event.type == pl.MOUSEMOTION:
            part = self.get_part_at(Pt(event.pos))
            if part:
                part.mouse_move(Pt(event.pos))
        elif event.type == pl.MOUSEBUTTONDOWN:
            part = self.get_part_at(Pt(event.pos))
            if part:
                part.click(Pt(event.pos), event.button)

        for p in self.parts:
            p.handle(event)

    def add(self, new_part):
        self.parts.append(new_part)

    def get_part_at(self, pos):
        for part in self.parts:
            if part.area.collidepoint(pos):
                return part

        return None

    def get_cursor_at(self, pos):
        part = self.get_part_at(Pt(pos))
        if part:
            return part.get_cursor(part_pos(part, pos))
        else:
            return None


def part_pos(part, pos):
    return Pt(pos) - part.area.topleft
