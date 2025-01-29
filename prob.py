import pygame
import pytmx

# Определите GID блоков, на которые нельзя наступать
UNWALKABLE_GIDS = {141, 81}  # Замените на реальные GID Ваших блоков


def is_walkable(x, y, tmx_data):
    # Проверяем, на каком слое мы находимся (например, на первом слое)
    layer = tmx_data.visible_layers[3]  # Замените на нужный слой
    gid = layer.get_tile_gid(x, y)  # Получаем GID блока по координатам
    return gid not in UNWALKABLE_GIDS  # Проверяем, можно ли пройти


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
    screen = pygame.display.set_mode((1000, 500))
    tmx_data = pytmx.load_pygame("map/1 уровень.tmx")
    clock = pygame.time.Clock()

    player_x, player_y = 7, 5  # Начальные координаты игрока

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and is_walkable(player_x, player_y - 1, tmx_data):
            player_y -= 1
        if keys[pygame.K_DOWN] and is_walkable(player_x, player_y + 1, tmx_data):
            player_y += 1
        if keys[pygame.K_LEFT] and is_walkable(player_x - 1, player_y, tmx_data):
            player_x -= 1
        if keys[pygame.K_RIGHT] and is_walkable(player_x + 1, player_y, tmx_data):
            player_x += 1

        screen.fill((0, 0, 0))
        draw_map(screen, tmx_data)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
