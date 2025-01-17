import os
import sys
import pygame

pygame.init()
size = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size)

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

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)

start_screen()
terminate()
