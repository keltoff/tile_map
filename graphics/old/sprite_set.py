import os.path as path
from ast import literal_eval as evaluate

import pygame

from auxiliary import Pt, SafeDict


class SpriteSet:
    def __init__(self, graphics=None, sprites=None):
        self.graphics = graphics
        self.rects = sprites
        self.graphic_file = None
        self.transparency = True

    def __getitem__(self, item):
        if item is tuple:
            return self.get_sprite(item[0], item[1])
        else:
            return self.get_sprite(item)

    def convert(self, target):
        self.graphics = self.graphics.convert_alpha(target)

    def get_sprite(self, key, subkey=None):
        if not subkey:
            if key.__class__ == tuple:
                key, subkey = key
            else:
                subkey = 0

        return self.graphics.subsurface(self.rects[key][subkey])

    def blit(self, target, destination, key, subkey=None):
        sprite = self.get_sprite(key, subkey)

        if destination.__class__ == pygame.Rect:
            center_pos = Pt(destination.center) - Pt(sprite.get_size()) / 2
        else:
            center_pos = Pt(destination) - Pt(sprite.get_size()) / 2
        target.blit(sprite, center_pos)

    def curse(self, target, position, key=None):
        rect, spot = self.cursors[key]
        target.blit(self.graphics, Pt(position) - spot, area=rect)

    def test_draw(self, target):
        target.blit(self.graphics, (0, 0))

        frame_col = (250, 0, 0)
        sec_col = (0, 250, 0)
        for sprite_val in self.rects.values():
            for img_val in sprite_val.values():
                pygame.draw.rect(target, sec_col, img_val, 2)
            pygame.draw.rect(target, frame_col, sprite_val[0], 2)

    def load_image(self, filename, transparency=None):
        img_file = path.join(sprite_dir, filename)
        self.graphics = pygame.image.load(img_file)
        self.graphic_file = filename

        self.transparency = False
        if transparency:
            if transparency in ['default', 'yes', 'True']:
                self.transparency = True
            elif transparency in ['no', 'False', 'None']:
                self.transparency = False
            elif transparency in ['top_left', 'topleft']:
                transparency = self.graphics.get_at((0, 0))
            elif transparency.__class__ == str:
                transparency = evaluate(transparency)

            if transparency.__class__ in [tuple, pygame.Color]:
                self.graphics.set_colorkey(transparency)
                self.transparency = 'key'

        return self.graphics
