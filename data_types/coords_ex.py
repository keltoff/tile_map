import operator
from .position import Dir


def add(xy1, xy2):
    x1, y1 = xy1
    x2, y2 = xy2
    return (x1+x2, y1+y2)


def neg(xy):
    x, y = xy
    return -x, -y


def mul(xy, k):
    x, y = xy
    return x*k, y*k


def div(xy, k):
    x, y = xy
    return x/k, y/k


class Pt(tuple):

    def __new__(self, *T, z=0, dir=Dir(0)):
        self.z = z
        self.dir = dir
        if len(T) == 1 and T[0].__class__ == tuple is tuple:
            return tuple.__new__(Pt, *T)
        else:
            return tuple.__new__(Pt, T)

    def __add__(self, other):
        return Pt(add(self, other), z=self.z, dir=self.dir)

    def __neg__(self):
        return Pt(neg(self), z=self.z, dir=self.dir)

    def __sub__(self, other):
        return self + neg(other)

    def __mul__(self, other):
        return Pt(mul(self, other), z=self.z, dir=self.dir)

    def __div__(self, other):
        return Pt(div(self, other), z=self.z, dir=self.dir)

    def __repr__(self):
        return '(x: {}, y: {})'.format(*self)


Pt.x = property(operator.itemgetter(0))
Pt.y = property(operator.itemgetter(1))
