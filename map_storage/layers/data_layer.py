from .base_layer import BaseLayer


class DataLayer(BaseLayer):
    def __init__(self, name, data, outside=None):
        h = len(data)
        w = len(data[0])

        super().__init__((w, h), name)

        self.data = data
        self.outside = outside

    def at(self, x, y):
        if self.is_inside(x, y):
            return self.data[y][x]
        else:
            return self.outside

    @classmethod
    def from_xml(cls, xml_node):
        return cls(name=xml_node.attrib['name'],
                   data=[s.strip() for s in xml_node.text.split()],
                   outside=xml_node.attrib.get('outside', None))
