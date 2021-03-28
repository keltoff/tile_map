class Widget:
    def __init__(self, area):
        self.area = area
        self.cursor = None

    def draw(self, surface):
        pass

    def get_cursor(self, pos):
        return self.cursor

    def handle(self, event):
        pass

    def click(self, pos, button):
        pass

    def mouse_move(self, pos):
        pass
