import os.path as path
import xml.etree.ElementTree as et
from ast import literal_eval as evaluate

import pygame

from auxiliary import Pt, SafeDict

sprite_dir = ''


def load(filename):
    root = et.parse(filename)
    gdata = root.find('./graphics').attrib

    img_file = path.join(path.dirname(filename), gdata['file'])

    result = SpriteSet()
    result.load_image(img_file, gdata.get('transparent', False))

    sprites = dict()
    for snode in root.findall('./sprite'):
        sprite = dict()
        sprites[snode.attrib['key']] = sprite
        for i, frame in enumerate(snode.findall('./img')):
            sprite[i] = pygame.Rect(evaluate(frame.attrib['rect']))
            if 'key' in frame.attrib:
                sprite[frame.attrib['key']] = sprite[i]

        for alias in snode.findall('./alias'):
            sprite[alias.attrib['key']] = sprite[alias.attrib['means']]

    for alias in root.findall('./alias'):
        sprites[alias.attrib['key']] = sprites[alias.attrib['means']]

    cursors = SafeDict()
    for cnode in root.findall('./cursor'):
        rect = pygame.Rect(evaluate(cnode.attrib['rect']))
        hotspot = Pt(evaluate(cnode.attrib.get('hotspot', (0, 0))))
        cdata = (rect, hotspot)
        cursors[cnode.attrib['key']] = cdata
        if cnode.attrib.get('default', False):
            cursors.default = cdata

    result.rects = sprites
    result.cursors = cursors
    return result


def save(sprite_set, filename):
    root = et.Element("set")

    transparency = '{}'.format(sprite_set.transparency)
    if transparency == 'key':
        transparency = '{}'.format(sprite_set.graphics.get_colorkey())
    et.SubElement(root, "graphics", file=sprite_set.graphic_file, transparent=transparency)

    previous = []
    for key in sprite_set.rects:
        add_sprite_node(root, key, sprite_set.rects[key], previous)

    tree = et.ElementTree(root)
    tree.write(filename)


def add_sprite_node(root, key, rect_dict, previous):
    if rect_dict in previous:
        # et.SubElement(root, 'alias', key=key, means=previous[rect_dict])
        pass
    else:
        snode = et.SubElement(root, 'sprite', key='{}'.format(key))
        previous.append(rect_dict)
        prev_imgs = []
        for sp_key in rect_dict:
            add_img_node(snode, sp_key, rect_dict[sp_key], prev_imgs)


def add_img_node(parent, key, rect, previous):
    if rect in previous:
        # et.SubElement(parent, 'alias', key=key, means=previous[key])
        pass
    else:
        et.SubElement(parent, 'img', rect=rect2str(rect), key='{}'.format(key))
        previous.append(rect)


def rect2str(rect):
    return '({}, {}, {}, {})'.format(rect.left, rect.top, rect.width, rect.height)


def slice_grid(img_file, tile_size, gap=0, margin=0, transparency=None):
    result = SpriteSet()
    graphic = result.load_image(img_file, transparency)
    w, h = graphic.get_size()

    i = 0
    sprites = dict()
    for ix, x in enumerate(range(margin, w - margin, tile_size + gap)):
        for iy, y in enumerate(range(margin, h - margin, tile_size + gap)):
            sprites[i] = {0: pygame.Rect(x, y, tile_size, tile_size)}
            sprites[(ix, iy)] = sprites[i]
            i += 1

    result.rects = sprites
    return result


def slice_smart(img_file):
    NotImplemented()

