from .base_layer import BaseLayer
from tile_map.data_types.position import Position


class ObjectLayer(BaseLayer):
    def __init__(self, size, name):
        super().__init__(size, name)

        self.objects_at_pos = dict()
        self.object_positions = dict()

    def objects(self):
        return self.object_positions.keys()

    def at(self, x, y):
        return self.objects_at_pos.get((x, y), [])

    def add(self, item, position):
        if position not in self.objects_at_pos:
            self.objects_at_pos[position] = []
        self.objects_at_pos[position].append(item)
        self.object_positions[item] = position

        item.pos = Position(*position)

    def add_many(self, item_position):
        for item, position in item_position.items():
            self.add(item, position)

    def move(self, item, position):
        if item in self.object_positions:
            self.objects_at_pos[item.pos].delete(item)

        self.add(item, position)

    def remove(self, item):
        if item in self.object_positions:
            self.objects_at_pos[item.pos.place].remove(item)
            # self.object_positions[item] = None
            self.object_positions.pop(item)
            item.pos = None
