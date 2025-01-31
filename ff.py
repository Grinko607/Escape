import os
import sys

import pygame
import pytmx

# Инициализация Pygame
pygame.init()

# Настройки экрана
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Перемещение по карте Tiled")

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

# Загрузка карты Tiled
tmx_data = pytmx.load_pygame('map/1 уровень.tmx')

# Загрузка изображения
player_image = load_image('z1.png')
player_rect = player_image.get_rect()

# Начальная позиция игрока
player_rect.topleft = (100, 100)

map_width = tmx_data.width * tmx_data.tilewidth
map_height = tmx_data.height * tmx_data.tileheight

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Отображение карты
    screen.fill((0, 0, 0))  # Очистка экрана
    for layer in tmx_data.visible_layers:
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= 5
    if keys[pygame.K_RIGHT]:
        player_rect.x += 5
    if keys[pygame.K_UP]:
        player_rect.y -= 5
    if keys[pygame.K_DOWN]:
        player_rect.y += 5

    # Отрисовка карты и игрока
    screen.fill((0, 0, 0))  # Очистка экрана
    for layer in tmx_data.visible_layers:
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    pygame.display.flip()


    pygame.time.delay(30)  # Задержка для управления FPS

pygame.quit()


