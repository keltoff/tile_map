from gui import Widget, Button
from graphics.sprite import Sprite
from data_types.coords_ex import Pt, Dir
import pygame


class CharacterOrganizer:
    def __init__(self):
        self.pcs = []
        self.npcs = []
        self.current = 0

    def add_pc(self, character):
        self.pcs.append(character)

    @property
    def current_pc(self):
        if len(self.pcs) <= self.current:
            return None
        else:
            return self.pcs[self.current]

    def prev(self):
        self.current -= 1
        if self.current < 0:
            self.current = len(self.pcs) - 1

    def next(self):
        self.current += 1
        if self.current >= len(self.pcs):
            self.current = 0


class CharacterDisplay(Widget):
    def __init__(self, area, character_set: CharacterOrganizer):
        super().__init__(area)

        self.characters = character_set

    def draw(self, surface):
        character = self.characters.current_pc

        pygame.draw.rect(surface, pygame.Color('White'), self.area, 1)

        character.draw(surface, Pt(self.area.centerx, self.area.bottom - 20, dir=Dir(1)))


class Switch(Widget):
    def __init__(self, area, label):
        super().__init__(area)
        self.color = pygame.Color('yellow')
        self.on = False
        self.cursor = 'hand'

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color('gray'), self.area, 2)

        if self.on:
            pygame.draw.rect(surface, self.color, self.area.inflate(-6, -6), 2)

    def click(self, pos, button):
        if button == 1:
            self.on = not self.on


class ActionSelect(Widget):
    def __init__(self, area, actions):
        super().__init__(area)

        self.actions = actions
        self.selected_idx = None

        button_h, button_w = 30, 60
        margin = 5

        first_btn_rect = pygame.Rect(self.area.left, self.area.top, button_w, button_h)
        self.buttons = [Switch(first_btn_rect.move(i * (button_w + margin), 0), a) for i, a in enumerate(actions)]

    def draw(self, surface):
        for b in self.buttons:
            b.draw(surface)

    def click(self, pos, button):
        if button == 1:
            for i, b in enumerate(self.buttons):
                if b.area.collidepoint(pos):
                    self.button_clicked(i)

    def button_clicked(self, idx):
        for i, b in enumerate(self.buttons):
            b.on = idx == i

        self.selected_idx = idx
        print(self.selected)

    @property
    def selected(self):
        if self.selected_idx is None:
            return None
        else:
            return self.actions[self.selected_idx]
