import pygame
import pytmx

def draw_map(screen, tmx_data):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))
        elif isinstance(layer, pytmx.TiledObjectGroup):
            for obj in layer:
                if obj.image:
                    screen.blit(obj.image, (obj.x, obj.y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 1000))
    tmx_data = pytmx.load_pygame("map/1 уровень.tmx")
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill((0, 0, 0))
        draw_map(screen, tmx_data)  # Рисуем карту
        pygame.display.flip()  # Обновляем экран
        clock.tick(60)  # Ограничиваем FPS

if __name__ == "__main__":
    main()
