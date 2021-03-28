from data_types.coords_ex import Pt


class Sprite:
    def __init__(self, img, pos):
        self.graphic = img
        self.pos = pos

    def draw(self, target, pt):
        self.graphic.draw(target, pt)


class DirectionSprite(Sprite):
    def __init__(self, frames, pos):
        Sprite.__init__(self, None, pos)
        self.frames = frames

    def draw(self, target, pt: Pt):
        self.frames[pt.dir.dir].draw(target, pt)
