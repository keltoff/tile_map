# from .storage import load_image
import pygame
import xml.etree.cElementTree as ET
# from lxml import etree as ET
import xml.dom.minidom
from itertools import product
from os.path import join


def iterate_over(array: pygame.PixelArray):
    w, h = array.surface.get_size()
    for y, x in product(range(h), range(w)):
        yield x, y


def raw_components(image: pygame.Surface):
    im_array = pygame.PixelArray(image)

    com_map = pygame.Surface(img.surface.get_size())
    components = pygame.PixelArray(com_map)

    neighbors = set()
    comps = 0

    for x, y in iterate_over(im_array):
        if image.unmap_rgb(im_array[x, y]) == (0, 0, 0, 255):  # is black
            components[x, y] = 0
        else:
            if x >= 1:
                l_comp = components[x - 1, y]
            else:
                l_comp = None

            if y >= 1:
                u_comp = components[x, y - 1]
            else:
                u_comp = None

            if l_comp and u_comp and l_comp != u_comp:
                neighbors.add((u_comp, l_comp))
            if l_comp:
                c = l_comp
            elif u_comp:
                c = u_comp
            else:
                comps += 1
                c = comps

            components[x, y] = c

    # each component is neighboring itself
    for c in range(1, comps + 1):
        neighbors.add((c, c))

    return components, neighbors


def group_connected_neghbors(neighbor_list):
    group_members = dict()
    group_allegiance = dict()
    group_allegiance[0] = 0  # ungrouped remain ungrouped
    group_count = 0
    for c1, c2 in neighbor_list:
        if c1 in group_allegiance and c2 in group_allegiance:
            g1, g2 = group_allegiance[c1], group_allegiance[c2]
            if g1 != g2:
                for c in group_members[g2]:
                    group_members[g1].append(c)
                    group_allegiance[c] = g1
                    group_members[g1].append(c2)
                    group_allegiance[c2] = g1
                group_members.pop(g2)
        elif c1 in group_allegiance:
            group = group_allegiance[c1]
            group_members[group].append(c2)
            group_allegiance[c2] = group
        elif c2 in group_allegiance:
            group = group_allegiance[c2]
            group_members[group].append(c1)
            group_allegiance[c1] = group
        else:
            group_count += 1
            group_members[group_count] = [c1, c2]
            group_allegiance[c1] = group_count
            group_allegiance[c2] = group_count

    return group_allegiance


def find_components(image):
    components, neighbors = raw_components(image)

    comps_to_groups = group_connected_neghbors(neighbors)

    for x, y in iterate_over(components):
        components[x, y] = comps_to_groups[components[x, y]]

    return components


def detect_bbs(components):
    bbs = dict()
    for x, y in iterate_over(components):
        c = components[x, y]
        if c > 0 and c in bbs:
            # update
            x0, y0, x1, y1 = bbs[c]
            x0 = min(x0, x)
            x1 = max(x1, x)
            y0 = min(y0, y)
            y1 = max(y1, y)
            bbs[c] = x0, y0, x1, y1
        else:
            bbs[c] = x, y, x, y
    return bbs


def box_size(bb):
    return  bb[2] - bb[0] + bb[3] - bb[1]


def form_grid(bounding_boxes, min_overlap=0.6):
    def top_left(bb_list):
        return sorted(bb_list, key=lambda bb: bb[0] + bb[1])[0]

    def y_overlaps(bb1, bb2):
        bb1_height = (bb1[3] - bb1[1])
        overlap_h = max(min(bb2[3] - bb1[1], bb1[3] - bb2[1]), 0)
        return overlap_h > bb1_height * min_overlap

    remaining_bb = bounding_boxes
    grid = []
    while remaining_bb:
        line_start = top_left(remaining_bb)
        top_line = list(filter(lambda bb: y_overlaps(bb, line_start) , remaining_bb))
        rest = list(filter(lambda bb: not y_overlaps(bb, line_start), remaining_bb))
        grid.append(sorted(top_line, key=lambda bb: bb[0]))
        remaining_bb = rest

    return grid


def save_image(file_name, image, bb_grid):
    pygame.font.init()
    myfont = pygame.font.SysFont('Tahoma', 8)

    out_img = image.copy()

    for iy, line in enumerate(bb_grid):
        for ix, bb in enumerate(line):
            x0, y0, x1, y1 = bb

            # draw to out_img
            bbox = pygame.Rect(x0, y0, x1 - x0 +1, y1 - y0 + 1)
            pygame.draw.rect(out_img, pygame.Color('red'), bbox, width=1)
            textsurface = myfont.render(f'{iy} - {ix}', False, pygame.Color('red'))
            out_img.blit(textsurface, (x0 + 2, y1 - 10))

    pygame.image.save(out_img, file_name)


def save_xml(xml_file_path, img_file_name, bb_grid):
    root = ET.Element("graphics")
    file_node = ET.SubElement(root, "file", path=img_file_name, transparent="top_left")

    for iy, line in enumerate(bb_grid):
        for ix, bb in enumerate(line):
            x0, y0, x1, y1 = bb

            ET.SubElement(file_node, "img", key=f'{prefix}_{iy}_{ix}',
                                            rect=f'({x0}, {y0}, {x1 - x0 +1}, {y1 - y0 + 1})',
                                            pt=f'({int((x0 + x1) / 2)}, {y1 - 5})')

    with open(xml_file_path, 'w') as file:
        xml_str = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml()
        file.write(xml_str)


if __name__ == '__main__':
    data_dir = '../../data/'
    img_file = 'jennifer.png'
    # img_file = 'warriorF.png'

    # prefix = 'jen2'
    prefix = img_file[:3]

    img = pygame.image.load(join(data_dir, img_file))

    components = find_components(img)

    # compute bbs
    bb_dict = detect_bbs(components)
    bounds = list([bb for group, bb in bb_dict.items() if 50 < box_size(bb) < 200])

    grid = form_grid(bounds, min_overlap=0.6)

    # output
    save_image(join(data_dir, f'{prefix}_sliced.png'), img, grid)
    save_xml(join(data_dir, f'{prefix}.xml'), img_file, grid)