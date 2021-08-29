import xml.etree.ElementTree as et
from ..data_types.position import Position
from ast import literal_eval as evaluate
from itertools import product


class MapStorage:
    def __init__(self):
        pass

    def tiles(self):
        return []


class MapSet:
    def __init__(self):
        self.maps = None
        self.terrain = None
        self.current = None
        self.start_position = None

    def __getitem__(self, item):
        # if isinstance(item, Tuple):
        #     map, pos = item
        #     return self.maps[map][pos]
        # else:
        return self.maps[item]

    def load(self, filename):
        data = et.parse(filename)

        self.maps = dict()
        for node in data.iterfind('./maps/floor'):
            floor_map = MapData.from_xml(node, self)
            self.maps[floor_map.name] = floor_map

        self.terrain = dict()
        for ter in data.findall('terrain'):
            att = ter.attrib
            self.terrain[att['key']] = TerrainType(att)

        # start_node = data.find('player')
        # self.current = start_node.attrib['map']
        # self.start_position = pos_from_xml(start_node)

    @property
    def actual(self):
        return self.maps.get(self.current)


class MapData:
    def __init__(self):
        # self.data = None
        self.layers = dict()
        # self.terrain = None
        self.state = dict()
        self.map_set = None
        self.name = None

    @property
    def data(self):
        return self.layers['terrain']

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return self.data[item]
        elif isinstance(item, Position):
            return self[item.x, item.y]
        else:
            return None

    def __iter__(self):
        for y, x in product(range(len(self.data)), range(len(self.data[0]))):
            ter = self.map_set.terrain[self.data[y][x]]
            state = self.state_at(Position(x, y))
            yield x, y, ter, state

    def tiles(self):
        for y, x in product(range(self.data.height), range(self.data.width)):
            pos = Position(x, y)
            ter = self.map_set.terrain[self.data[x, y]]
            state = self.state_at(pos)
            data = {l_name: self.layers[l_name][pos] for l_name in self.layers}
            data['color'] = ter['color']
            pos.z = int(data.get('height', 0))
            yield pos, ter, data, state

    def center(self):
        return Position(int(self.width / 2), int(self.height / 2))

    @staticmethod
    def from_xml(node, mapset):
        new = MapData()
        # new.data = [s.strip() for s in node.find('data').text.split()]
        new.layers = {l.name: l for l in (Layer.from_xml(ln) for ln in node.findall('layer'))}
        new.map_set = mapset
        new.name = node.attrib['name']
        return new

    # def load(self, filename):
    #     data = et.parse(filename)
    #     self.data = [s.strip() for s in data.find('data').text.split()]
    #
    #     self.out_terrain = data.find('data').attrib['outside']
    #
    #     self.terrain = dict()
    #     for ter in data.findall('terrain'):
    #         att = ter.attrib
    #         self.terrain[att['key']] = TerrainType(att)
    #
    #     #self.monsters = [Monster(m.attrib) for m in data.findall('.//places/monster')]

    @property
    def width(self):
        return self.data.width

    @property
    def height(self):
        return self.data.height

    def terrain_at(self, pos):
        ter = self[pos]
        if ter:
            return self.map_set.terrain[ter]
        else:
            return None

    def state_at(self, pos):
        key = (pos.x, pos.y)
        if key not in self.state:
            self.state[key] = MapState()
        return self.state[key]

    def mark_visible(self, pos):
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                self.state_at(pos.shifted(x, y)).visible = True

    def is_different(self, x, y, ter):
        if 0 <= y < len(self.data) and 0 <= x < len(self.data[y]):
            return self.data[x, y] != ter['key']
        else:
            return False


class TerrainType:
    def __init__(self, attributes):
        self.stats = attributes
        self.stats['color'] = evaluate(attributes['color'])

    def __getitem__(self, item):
        return self.stats[item]

    @property
    def free(self):
        return self['free'] in ['true', 'True', '1', True]

    def get_b(self, index):
        return self.stats.get(index, False) in ['true', 'True', '1', True]

    def get_n(self, index):
        return int(self.stats.get(index, 0))



class MapState:
    def __init__(self, attributes=None):
        self.stats = attributes if attributes else dict()

    @property
    def visible(self):
        return self.stats.get("visible", False)

    @visible.setter
    def visible(self, val):
        self.stats["visible"] = val


class Layer:
    def __init__(self):
        self.name = None
        self.data = None
        self.outside = None

    def __getitem__(self, item):
        if isinstance(item, tuple):
            x, y = item
            if len(self.data) > y and len(self.data[y]) > x:
                return self.data[y][x]
            else:
                return self.outside
        elif isinstance(item, Position):
            return self[item.x, item.y]
        else:
            return None

    @property
    def width(self):
        return len(self.data[0])

    @property
    def height(self):
        return len(self.data)

    @staticmethod
    def from_xml(node):
        new = Layer()
        new.data = [s.strip() for s in node.text.split()]
        new.name = node.attrib['name']
        new.outside = node.attrib.get('outside', None)
        return new


def pos_from_xml(node):
    return Position(**{key: int(node.attrib[key]) for key in ['x', 'y', 'd']})
