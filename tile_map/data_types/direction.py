
class Dir:  #(int):
    def __init__(self, init_dir=0):
        if isinstance(init_dir, Dir):
            init_dir = init_dir.dir

        self.dir = init_dir

    def angle(self):
        return -90 * self.dir

    def __add__(self, other):
        return Dir((self.dir + other) % 4)

    def __sub__(self, other):
        return self.__add__(-other)

    def __eq__(self, other):
        if isinstance(other, Dir):
            return self.dir == other.dir
        elif isinstance(other, int):
            return self.dir == other
        else:
            return False

    def shift(self):
        if self.dir == 0:
            return 0, -1
        if self.dir == 1:
            return 1, 0
        if self.dir == 2:
            return 0, 1
        if self.dir == 3:
            return -1, 0
        raise Exception('Invalid Dir instance', self.dir)

    def __str__(self):
        if self.dir == 0:
            return 'A'
        if self.dir == 1:
            return '>'
        if self.dir == 2:
            return 'V'
        if self.dir == 3:
            return '<'
        raise Exception('Invalid Dir instance', self.dir)

    def lt(self):
        return self - 1

    def rt(self):
        return self + 1

    @staticmethod
    def up():
        return Dir(0)

    @staticmethod
    def right():
        return Dir(1)

    @staticmethod
    def down():
        return Dir(2)

    @staticmethod
    def left():
        return Dir(3)