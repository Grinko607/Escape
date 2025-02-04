import os
import sys
import pygame
import pytmx

def init_game(screen_width, screen_height):
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Отображение карты Tiled по центру")
    return screen

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

def load_map(filename):
    return pytmx.load_pygame(filename)

def center_camera(screen_width, screen_height, map_width, map_height):
    camera_x = (screen_width - map_width) // 2
    camera_y = (screen_height - map_height) // 2
    return camera_x, camera_y

def draw_map(screen, tmx_data, camera_x, camera_y):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth + camera_x, y * tmx_data.tileheight + camera_y))

def draw_start_button(screen, screen_width, screen_height):
    button_width = 200
    button_height = 100
    button_x = (screen_width - button_width) // 2
    button_y = (screen_height - button_height) // 2

    # Рисуем серый прямоугольник
    pygame.draw.rect(screen, (169, 169, 169), (button_x, button_y, button_width, button_height))

    # Настройка шрифта
    font = pygame.font.Font(None, 36)
    text = font.render("Старт", True, (0, 0, 0))
    text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

def regist():
    print("Функция regist вызвана!")

def main():
    screen_width = 1280
    screen_height = 720
    screen = init_game(screen_width, screen_height)

    begin = load_map('map/проект оч важно.tmx')
    map_width = begin.width * begin.tilewidth
    map_height = begin.height * begin.tileheight
    camera_x, camera_y = center_camera(screen_width, screen_height, map_width, map_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if (screen_width // 2 - 100 < mouse_x < screen_width // 2 + 100) and (screen_height // 2 - 50 < mouse_y < screen_height // 2 + 50):
                    regist()

        screen.fill((0, 0, 0))
        draw_map(screen, begin, camera_x, camera_y)
        draw_start_button(screen, screen_width, screen_height)

        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()

if __name__ == "__main__":
    main()





