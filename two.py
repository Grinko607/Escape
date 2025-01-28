import pytmx
import pygame

pygame.init()

tmx_data = pytmx.load_pygame('1 уровень.tmx')
screen_width = tmx_data.width * tmx_data.tilewidth
screen_height = tmx_data.height * tmx_data.tileheight
screen = pygame.display.set_mode((screen_width, screen_height))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    for layer in tmx_data.visible_layers:
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    pygame.display.flip()

pygame.quit()
