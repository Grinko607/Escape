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

cursor_image = load_image('курсор.jpg')
cursor_size = cursor_image.get_size()
cursor = pygame.cursors.Cursor((0, 0), cursor_image)
pygame.mouse.set_cursor(cursor)
characters = [
    load_image('ch1.jpg'),
    load_image('l1.jpg'),
    load_image('o1.jpg'),
    load_image('z1.png')
]

animation_frames = {
    0: [load_image('z2.png'), load_image('z3.png'), load_image('z4.png'), load_image('z5.png')],
    1: [load_image('ch2.jpg'), load_image('ch3.jpg')],
    2: [load_image('l2.jpg'), load_image('l3.jpg'), load_image('l4.jpg'), load_image('l5.jpg')],
    3: [load_image('o2.jpg'), load_image('o3.jpg')]
}

current_index = 0
current_frame = 0
animation_speed = 5
frame_counter = 0


def change_character(direction):
    global current_index, current_frame
    current_index = (current_index + direction) % len(characters)
    current_frame = 0


def draw_characters(window):
    global current_frame, frame_counter
    window.fill((255, 255, 255))

    left_index = (current_index - 1) % len(characters)
    right_index = (current_index + 1) % len(characters)

    frame_counter += 1
    if frame_counter >= animation_speed:
        current_frame = (current_frame + 1) % len(animation_frames[current_index])
        frame_counter = 0

    scale_factor = 4
    left_image = pygame.transform.scale(animation_frames[left_index][current_frame % len(animation_frames[left_index])],
                                        (int(animation_frames[left_index][current_frame % len(
                                            animation_frames[left_index])].get_width() * scale_factor),
                                         int(animation_frames[left_index][current_frame % len(
                                             animation_frames[left_index])].get_height() * scale_factor)))

    center_image = pygame.transform.scale(animation_frames[current_index][current_frame],
                                          (int(animation_frames[current_index][
                                                   current_frame].get_width() * scale_factor),
                                           int(animation_frames[current_index][
                                                   current_frame].get_height() * scale_factor)))

    right_image = pygame.transform.scale(
        animation_frames[right_index][current_frame % len(animation_frames[right_index])],
        (int(animation_frames[right_index][
                 current_frame % len(animation_frames[right_index])].get_width() * scale_factor),
         int(animation_frames[right_index][
                 current_frame % len(animation_frames[right_index])].get_height() * scale_factor)))

    left_pos = (WIDTH // 3 - 150 - left_image.get_width() // 2, HEIGHT // 2 - 100)
    center_pos = (WIDTH // 2 + 50- center_image.get_width() // 2, HEIGHT // 2 - 250)
    right_pos = (2 * WIDTH // 3 + 200 - right_image.get_width() // 2, HEIGHT // 2 - 100)

    window.blit(left_image, left_pos)
    window.blit(center_image, center_pos)
    window.blit(right_image, right_pos)


FPS = 50
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def open_new_window():
    new_window_size = (1280, 720)
    new_window = pygame.display.set_mode(new_window_size)
    pygame.display.set_caption("Персонажи")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if mouse_x < WIDTH // 3:
                    change_character(-1)
                elif mouse_x > 2 * WIDTH // 3:
                    change_character(1)
        draw_characters(new_window)
        pygame.display.flip()
        clock.tick(FPS)


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
                open_new_window()
                return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
terminate()
