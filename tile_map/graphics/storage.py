import os.path as path
import xml.etree.ElementTree as et
from ast import literal_eval as evaluate
from .sprite import Sprite, DirectionSprite, IsoSprite
from ..data_types.position import Position
from ..data_types.coords_ex import Pt
import pygame
import pygame.transform
from copy import copy

# from auxiliary import Pt, SafeDict


class Graphic:
    def __init__(self, img, origin):
        self.img = img
        self.origin = origin

    def draw(self, target_surface, pt):
        target_surface.blit(self.img, pt - self.origin)

    def flip(self, h=False, v=False):
        if h:
            x = self.img.get_width() - self.origin.x
        else:
            x = self.origin.x

        if v:
            y = self.img.get_height() - self.origin.y
        else:
            y = self.origin.y

        return Graphic(pygame.transform.flip(self.img, h, v), Pt(x, y))


class Loop:
    def __init__(self, times: [int], frames: [Graphic], looped=True):
        self.frames = frames
        self.times = times
        self.looped = looped

        self.t = 0
        self.frame_idx = 0

    def draw(self, target_surface, pt):
        # self.update(blah)

        self.frames[self.frame_idx].draw(target_surface, pt)

    def update(self, ms):
        self.t += ms

        while self.t >= self.times[self.frame_idx]:
            if self.done():
                if self.looped:
                    self.frame_idx = 0
                else:
                    self.t = self.times[self.frame_idx]
                    break

            self.t -= self.times[self.frame_idx]
            self.frame_idx += 1

    def done(self):
        return self.frame_idx == len(self.frames) -1 and self.t >= self.times[self.frame_idx]

    def clone(self, reverse=False):
        if reverse:
            frames = [f.flip(h=True) for f in self.frames]
        else:
            frames = self.frames
        return Loop(self.times, frames, self.looped)


class Storage:
    def __init__(self):
        self.graphics = dict()
        self.sprites = dict()

    def __getitem__(self, item):
        return self.graphics[item]

    def make_sprite(self, key, initial_pos):
        sprite = copy(self.sprites[key])
        sprite.pos = initial_pos
        return sprite

    @staticmethod
    def load(filename):
        result = Storage()

        gdata = et.parse(filename)

        for g_file in gdata.findall('file'):
            img_file = path.join(path.dirname(filename), g_file.attrib['path'])
            img = load_image(img_file, g_file.attrib.get('transparent', False))
            # store in storage?

            for img_node in g_file.findall('img'):
                rect = pygame.Rect(evaluate(img_node.attrib['rect']))
                result.graphics[img_node.attrib['key']] = Graphic(img.subsurface(rect), Pt(evaluate(img_node.attrib['pt'])))

        for sprite_node in gdata.findall('sprite'):
            result.sprites[sprite_node.attrib['key']] = result.parse_sprite(sprite_node)

        return result

    def parse_sprite(self, node):
        type = node.attrib.get('type', 'flat')
        pattern = node.get('pattern', node.attrib['key'])
        pos = Position(0, 0)

        if type == 'flat':
            return Sprite(self[pattern], pos)
        elif type == 'iso':
            frames = {int(n.attrib['dir']): self.load_graphic(pattern.format(subkey=n.attrib['subkey']),
                                                              n.attrib.get('hflip') == 'True')
                      for n in node.findall('frame')}

            return DirectionSprite(frames, pos)
        elif type == 'rotated':
            frames = {dir: self[pattern].rotate(90 * dir) for dir in range(4)}
            return DirectionSprite(frames, pos)

        elif type == 'animated':
            loops = {loop_node.attrib['key']: self.parse_loop(loop_node)  for loop_node in node.findall('loop')}
            modes = [mode_node.text for mode_node in node.findall('mode')]
            return IsoSprite(loops, pos, modes)

    def load_graphic(self, key, h_flip=False):
        img = self[key]
        if h_flip:
            # img = pygame.transform.flip(img, h_flip, False)
            img = img.flip(h=h_flip)
        return img

    def parse_loop(self, node):
        times, frame_keys, flipped = zip(*[(int(n.attrib['t']),
                                            n.attrib['key'],
                                            n.attrib.get('reversed', False) in ['True', 'true'])
                                           for n in node.findall('frame')])
        frames = [self.load_graphic(key, h_flip=flip) for key, flip in zip(frame_keys, flipped)]
        return Loop(times, frames, node.attrib.get('looped', False))


def load_image(filename, transparency=None):
    img = pygame.image.load(filename)

    if transparency in ['top_left', 'topleft']:
        transparency = img.get_at((0, 0))

    img.set_colorkey(transparency)
    return img
