import os
import sys
import pygame

pygame.init()
size = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size)


def open_new_window():
    new_window_size = (1280, 720)
    new_window = pygame.display.set_mode(new_window_size)
    pygame.display.set_caption("Персонажи")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if mouse_x < WIDTH // 3:
                    change_character(-1)
                elif mouse_x > 2 * WIDTH // 3:
                    change_character(1)

        draw_characters(new_window)
        pygame.display.flip()

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

characters = [
    load_image('ch1.jpg'),
    load_image('l1.jpg'),
    load_image('o1.jpg'),
    load_image('z1.png')
]

current_index = 1

def change_character(direction):
    global current_index
    current_index = (current_index + direction) % len(characters)

def draw_characters(window):
    window.fill((255, 255, 255))
    left_index = (current_index - 1) % len(characters)
    right_index = (current_index + 1) % len(characters)
    left_pos = (WIDTH // 3 - characters[left_index].get_width() // 2, HEIGHT // 2)
    center_pos = (WIDTH // 2 - characters[current_index].get_width() // 2, HEIGHT // 2)
    right_pos = (2 * WIDTH // 3 - characters[right_index].get_width() // 2, HEIGHT // 2)

    window.blit(characters[left_index], left_pos)
    window.blit(characters[current_index], center_pos)
    window.blit(characters[right_index], right_pos)

FPS = 50
clock = pygame.time.Clock()

def terminate():
    pygame.quit()
    sys.exit()

def start_screen():
    screen.fill((105, 105, 105))
    image = load_image('pixil-frame-0.png')
    image_size = (740, 680)
    scaled_image = pygame.transform.scale(image, image_size)
    image_rect = scaled_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(scaled_image, image_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if mouse_y > 250:
                    open_new_window()
                return
        pygame.display.flip()
        clock.tick(FPS)

start_screen()
terminate()
