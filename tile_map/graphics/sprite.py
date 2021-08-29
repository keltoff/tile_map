from ..data_types.coords_ex import Pt, Dir


class Sprite:
    def __init__(self, img, pos):
        self.graphic = img
        self.pos = pos
        self.pawn = None  # TODO move to descendant class

    def draw(self, target, pt):
        self.graphic.draw(target, pt)

    def update(self, time):
        pass


class DirectionSprite(Sprite):
    def __init__(self, frames, pos):
        Sprite.__init__(self, None, pos)
        self.frames = frames

    def draw(self, target, pt: Pt):
        self.frames[pt.dir.dir].draw(target, pt)


class IsoSprite:
    def __init__(self, loops, pos, modes):
        self.loops = loops
        self.modes = modes
        self.current_mode = None
        self.current_loop = None
        self._pos_ = pos

        self.set_mode(self.modes[0])

    def draw(self, target, pt):
        self.current_loop.draw(target, pt)

    def update(self, time):
        self.current_loop.update(time)

    @property
    def pos(self):
        return self._pos_

    @pos.setter
    def pos(self, value):
        # print(f'Pos update {self._pos_} to {value}')
        dir_changed = value.dir != self._pos_.dir
        self._pos_ = value

        if dir_changed:
            self.set_mode(self.current_mode)

    def set_mode(self, mode):
        if mode not in self.modes:
            raise Exception(f'Mode {mode} not known for this sprite.')

        self.current_mode = mode

        if self.pos.dir in [Dir.right(), Dir.down()]:
            sprite_dir = 'f'
        else:
            sprite_dir = 'r'

        reversed = self.pos.dir in [Dir.up(), Dir.right()]

        loop_key = f'{mode}_{sprite_dir}'
        # rev_flag = '[reversed]' if reversed else ''
        # print(f'Using loop {loop_key} {rev_flag}')
        self.current_loop = self.loops[loop_key].clone(reversed)
