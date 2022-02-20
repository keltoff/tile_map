import data_types.position as pos


class MapSprite:
    def __init__(self, x=0, y=0, img=None, d=0):
        self.pos = pos.Position(x=x, y=y, d=d)
        self.img = img

    def blit(self, pos):
        pass