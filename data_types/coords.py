import operator


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
    def __new__(self, *T):
        if len(T) == 1 and T[0].__class__ == tuple is tuple:
            return tuple.__new__(Pt, *T)
        else:
            return tuple.__new__(Pt, T)

    def __add__(self, other):
        return Pt(add(self, other))

    def __neg__(self):
        return Pt(neg(self))

    def __sub__(self, other):
        return self + neg(other)

    def __mul__(self, other):
        return Pt(mul(self, other))

    def __div__(self, other):
        return Pt(div(self, other))

    def __repr__(self):
        return '(x: {}, y: {})'.format(*self)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]
