import pygame.draw
from pygame import Color, Rect
from auxiliary import Pt


def draw(surface, pos, value, style):
    symbols = to_symbols(value)
    pos = Pt(pos)
    for s in symbols:
        pos = draw_symbol(surface, pos, s, style)


def draw_symbol(surface, pos, symbol, style):
    color = style_color(style)

    def bar(w):
        pygame.draw.rect(surface, color, Rect(pos, (w, 10)))
        return w + 2

    if symbol == 'x':
        d = bar(20)
    elif symbol == 'v':
        d = bar(10)
    elif symbol == 'i':
        d = bar(2)
    else:
        d = 0

    return pos + (d, 0)


def style_color(style):
    return Color(style)


def to_symbols(number):
    result = ''

    def convert(r, n, x, ch):
        r += ch * (n / x)
        n -= n / x * x
        return r, n

    result, number = convert(result, number, 10, 'x')
    result, number = convert(result, number, 5, 'v')
    result, number = convert(result, number, 1, 'i')

    return result
