import pygame
from .map_storage.map_storage import MapSet
from .map_display import OrthoSketch, IsoSketch
from .data_types.zone import Zone
from .data_types.position import Position as Pos
from .graphics.storage import Storage

if __name__ == '__main__':
    pygame.init()

    display = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()

    map_store = MapSet()
    map_store.load('data/mapdata.xml')

    sprite_storage = Storage.load('data/graphics_iso.xml')

    w, h = display.get_rect().size
    margin = 20
    rec1 = pygame.Rect(margin, margin, w / 2 - 2* margin, h - 2* margin)
    rec2 = pygame.Rect(margin + w / 2, margin, w / 2 - 2 * margin, h - 2 * margin)

    disp = OrthoSketch(display.subsurface(rec1), map_store['default'], tile_size=30)
    disp2 = IsoSketch(display.subsurface(rec2), map_store['default'], tile_size=30, tilt=60)

    disp2.sprites.append(sprite_storage.make_sprite('war', Pos(13, 5, d=0)))
    disp2.sprites.append(sprite_storage.make_sprite('war', Pos(11, 4, d=1)))
    disp2.sprites.append(sprite_storage.make_sprite('war', Pos(12, 3, d=2)))
    disp2.sprites.append(sprite_storage.make_sprite('war', Pos(14, 4, d=3)))

    disp2.sprites.append(sprite_storage.make_sprite('jen', Pos(3, 5, d=0)))
    disp2.sprites.append(sprite_storage.make_sprite('jen', Pos(1, 4, d=1)))
    disp2.sprites.append(sprite_storage.make_sprite('jen', Pos(2, 3, d=2)))
    disp2.sprites.append(sprite_storage.make_sprite('jen', Pos(4, 4, d=3)))

    disp.zones.append(Zone(positions=[Pos(13, 4), Pos(13, 5), Pos(14, 4), Pos(14, 5)], color=pygame.Color(0, 255, 0, 50)))
    disp2.zones.append(Zone(positions=[Pos(13, 4), Pos(13, 5), Pos(14, 4), Pos(14, 5)], color=pygame.Color(255, 0, 0, 50)))

    # disp.event_pos = lambda pos, etype, button: print('Event at pos {}'.format(pos)) if etype == pygame.MOUSEBUTTONDOWN else ''
    # disp2.event_pos = lambda pos, etype, button: print('Event2 at pos {}'.format(pos)) if etype == pygame.MOUSEBUTTONDOWN else ''

    # ss = sprite_load('data/arrows.xml')
    # you = MapSprite(3, 3, ss['you'])
    # them = [MapSprite(i, 4, ss['it'], 2) for i in range(4, 7)]

    game_over = False
    while not game_over:

        display.fill((0, 0, 0))

        # draw
        disp.draw()
        disp2.draw()

        pygame.display.flip()
        clock.tick(15)

        for event in pygame.event.get():
            disp.handle(event)
            disp2.handle(event)

            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over = True
                if event.key == pygame.K_LEFT:
                    pass
                if event.key == pygame.K_RIGHT:
                    pass
                if event.key == pygame.K_UP:
                    pass
