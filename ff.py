import pygame
import os

from птро import load_image

# Инициализация Pygame
pygame.init()

# Настройки экрана
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Загрузка тайлов
tile_size = 32
map_folder = 'map'
tiles = {}
for filename in os.listdir(map_folder):
    if filename.endswith('.png'):
        tile_name = filename[:-4]  # Убираем .png
        tiles[tile_name] = pygame.image.load(os.path.join(map_folder, filename))

# Персонаж
player_image = load_image('.png')
player_pos = [100, 100]  # Начальная позиция персонажа

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Управление персонажем
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= 5
    if keys[pygame.K_RIGHT]:
        player_pos[0] += 5
    if keys[pygame.K_UP]:
        player_pos[1] -= 5
    if keys[pygame.K_DOWN]:
        player_pos[1] += 5

    # Обновление камеры
    camera_x = player_pos[0] - screen_width // 2
    camera_y = player_pos[1] - screen_height // 2

    # Отрисовка карты и персонажа
    screen.fill((0, 0, 0))  # Очистка экрана
    for y in range(0, screen_height, tile_size):
        for x in range(0, screen_width, tile_size):
            # Здесь можно добавить логику для выбора тайла
            screen.blit(tiles['grass'], (x, y))  # Пример: отрисовка травы

    # Отрисовка персонажа
    screen.blit(player_image, (player_pos[0] - camera_x, player_pos[1] - camera_y))

    pygame.display.flip()

pygame.quit()

