from .direction import Dir


class Position:
    def __init__(self, x=0, y=0, z=0, d=Dir(0)):
        self.x = x
        self.y = y
        self.z = z
        self.dir = Dir(d)

    def __copy__(self):
        return Position(self.x, self.y, self.z, self.dir)

    def shifted(self, dx, dy, dz=0):
        new_pos = self.__copy__()
        new_pos.x += dx
        new_pos.y += dy
        new_pos.z += dz
        return new_pos

    def fwd(self):
        return self.shifted(*self.dir.shift())

    def bwd(self):
        return self.shifted(*(self.dir + Dir.down()).shift())

    def lt(self):
        return self.shifted(*(self.dir + Dir.left()).shift())

    def rt(self):
        return self.shifted(*(self.dir + Dir.right()).shift())

    def same_place(self, other):
        if other is None:
            return False
        else:
            return self.x == other.x and self.y == other.y

    def __str__(self):
        return '<{x}, {y}{z}> - {d}'.format(x=self.x, y=self.y, d=self.dir, z=', ^{}'.format(self.z) if self.z else '')
