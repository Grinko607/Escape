import os
import sqlite3
import sys
import pygame
import pytmx

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


def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load('music.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


def save_settings(volume, brightness, user_login):
    print(user_login)
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM регистрация WHERE Логин = ?', (user_login,))
    result = cursor.fetchone()
    user_id = result[0]
    cursor.execute('CREATE TABLE IF NOT EXISTS settings (id_user INTEGER, volume REAL, brightness REAL)')
    cursor.execute('DELETE FROM settings WHERE id_user = ?', (user_id,))
    cursor.execute('INSERT INTO settings (id_user, volume, brightness) VALUES (?, ?, ?)', (user_id, volume, brightness))

    conn.commit()
    conn.close()


def load_settings(user_login):
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM регистрация WHERE Логин = ?', (user_login,))
    result = cursor.fetchone()
    if result is None:
        return 0.5, 0.5
    user_id = result[0]
    cursor.execute('SELECT volume, brightness FROM settings WHERE id_user = ?', (user_id,))
    settings = cursor.fetchone()
    if settings is None:
        return 0.5, 0.5

    return settings


def settings_window(user_login):
    global volume, brightness
    pygame.init()
    screen = pygame.display.set_mode((600, 500))
    clock = pygame.time.Clock()
    volume, brightness = load_settings(user_login)
    pygame.mixer.music.set_volume(volume)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_settings(volume, brightness, user_login)
                    print(user_login)
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if 50 < mouse_x < 550:
                        if 150 < mouse_y < 180:
                            volume = (mouse_x - 50) / 500
                            pygame.mixer.music.set_volume(volume)
                        elif 250 < mouse_y < 280:
                            brightness = (mouse_x - 50) / 500

        screen.fill((int(200 * brightness), int(200 * brightness), int(200 * brightness)))
        pygame.draw.rect(screen, (255, 0, 0), (50, 150, 500, 30))
        pygame.draw.rect(screen, (0, 255, 0), (50, 250, 500, 30))
        pygame.draw.rect(screen, (0, 0, 0), (50 + volume * 500 - 5, 150, 10, 30))
        pygame.draw.rect(screen, (0, 0, 0), (50 + brightness * 500 - 5, 250, 10, 30))
        font = pygame.font.Font(None, 36)
        volume_text = font.render(f'Громкость: {int(volume * 100)}%', True, (0, 0, 0))
        brightness_text = font.render(f'Яркость: {int(brightness * 100)}%', True, (0, 0, 0))
        screen.blit(volume_text, (50, 120))
        screen.blit(brightness_text, (50, 220))

        button_rect = pygame.Rect(200, 300, 200, 50)
        pygame.draw.rect(screen, (255, 255, 255), button_rect)
        button_text = font.render('Перейти в игру', True, (0, 0, 0))
        screen.blit(button_text, (button_rect.x + 5, button_rect.y + 5))

        if button_rect.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
            save_settings(volume, brightness, user_login)
            startgame(volume, brightness, user_login)
            print(user_login)
            game(volume, brightness, user_login)

        pygame.display.flip()
        clock.tick(60)



play_music()
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


def load_character_from_db(user_id):
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('SELECT character_id FROM персонажи WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def draw_characters(window, user_login):
    global current_index, frame_counter
    window.fill((255, 255, 255))
    current_frame = 0

    # Загрузка выбранного персонажа
    user_id = get_user_id(user_login)  # Предполагается, что эта функция возвращает ID пользователя
    selected_character_id = load_character_from_db(user_id)

    if selected_character_id is not None:
        current_index = selected_character_id  # Установить индекс выбранного персонажа

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
    center_pos = (WIDTH // 2 + 40 - center_image.get_width() // 2, HEIGHT // 2 - 250)
    right_pos = (2 * WIDTH // 3 + 200 - right_image.get_width() // 2, HEIGHT // 2 - 100)

    window.blit(left_image, left_pos)
    window.blit(center_image, center_pos)
    window.blit(right_image, right_pos)

    # Рисуем кнопку "Сохранить"
    save_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 100, 100, 50)
    pygame.draw.rect(window, (200, 200, 200), save_button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render('Сохранить', True, (0, 0, 0))
    window.blit(text, (save_button_rect.x + 10, save_button_rect.y + 10))

    return save_button_rect


def save_character_to_db(user_id, character_id):
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM персонажи WHERE user_id = ?', (user_id,))  # Удаляем старый выбор, если есть
    cursor.execute('''
    INSERT INTO персонажи (user_id, character_id)
    VALUES (?, ?);
    ''', (user_id, character_id))
    conn.commit()
    conn.close()


def run_game(user_login):
    global window, save_button_rect
    FPS = 50
    clock = pygame.time.Clock()
    running = True
    window = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Игра")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    change_character(-1)
                elif event.key == pygame.K_RIGHT:
                    change_character(1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if save_button_rect.collidepoint(pos):
                        user_id = get_user_id(user_login)
                        save_character_to_db(user_id, current_index)

    pygame.quit()


def get_user_id(user_login):
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM регистрация WHERE Логин = ?', (user_login,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None





FPS = 50
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def open_new_window(user_login):
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
        draw_characters(new_window, user_login)
        pygame.display.flip()
        clock.tick(60)


def startgame(volume, brightness, user_login):
    screen.fill((105, 105, 105))
    image = load_image('pixil-frame-0.png')
    pygame.mixer.music.set_volume(volume)
    image_size = (740, 680)
    scaled_image = pygame.transform.scale(image, image_size)
    image_rect = scaled_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(scaled_image, image_rect)
    button1_rect = pygame.Rect(300, 110, 700, 100)
    button2_rect = pygame.Rect(300, 215, 700, 100)
    button3_rect = pygame.Rect(300, 340, 700, 100)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if button1_rect.collidepoint(mouse_pos):
                        game()
                        return
                    elif button2_rect.collidepoint(mouse_pos):
                        settings_window(user_login)
                        print(user_login)
                        return
                    elif button3_rect.collidepoint(mouse_pos):
                        open_new_window(user_login)
                        return

        pygame.display.flip()
        clock.tick(FPS)



def save_to_db(user_texts):
    print('a')
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO регистрация (Имя, Логин, пароль) VALUES (?, ?, ?)''',
                   (user_texts[0], user_texts[1], user_texts[2]))
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id


def regist():
    screen.fill((200, 200, 200))
    image = load_image('img.png')
    image = pygame.transform.scale(image, (600, 500))
    image_rect = image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    base_font = pygame.font.Font(None, 32)
    user_texts = ['', '', '']
    input_rects = [pygame.Rect(468, 140, 200, 32),
                   pygame.Rect(468, 248, 200, 24),
                   pygame.Rect(468, 196, 200, 24)]
    active_index = -1
    buttonfuture = pygame.Rect(670, 380, 200, 50)
    buttonpast = pygame.Rect(390, 380, 200, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttonfuture.collidepoint(event.pos):
                    user_login = user_texts[1]
                    volume = 0.5
                    brightness = 0.5
                    startgame(volume, brightness, user_login)
                    save_to_db(user_texts)
                    print('zzz')  # Передаем user_id в функцию старта игры
                elif buttonpast.collidepoint(event.pos):
                    main()
                for i, rect in enumerate(input_rects):
                    if rect.collidepoint(event.pos):
                        active_index = i
                        break
                    else:
                        active_index = -1
            if event.type == pygame.KEYDOWN and active_index != -1:
                if event.key == pygame.K_BACKSPACE:
                    user_texts[active_index] = user_texts[active_index][:-1]
                else:
                    user_texts[active_index] += event.unicode

        screen.blit(image, image_rect.topleft)

        for i, rect in enumerate(input_rects):
            text_surface = base_font.render(user_texts[i], True, (0, 0, 0))
            screen.blit(text_surface, (rect.x + 5, rect.y + 5))
            rect.w = max(100, text_surface.get_width() + 10)

        pygame.display.flip()
        clock.tick(60)



def load_map(filename):
    return pytmx.load_pygame(filename)


def draw_map(screen, tmx_data, camera_x, camera_y):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth + camera_x, y * tmx_data.tileheight + camera_y))


def center_camera(screen_width, screen_height, map_width, map_height):
    camera_x = (screen_width - map_width) // 2
    camera_y = (screen_height - map_height) // 2
    return camera_x, camera_y


def draw_button(screen, text, x, y, width, height):
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height))
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


def main():
    begin = load_map('map/проект оч важно.tmx')
    map_width = begin.width * begin.tilewidth
    map_height = begin.height * begin.tileheight
    camera_x, camera_y = center_camera(WIDTH, HEIGHT, map_width, map_height)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if (WIDTH // 2 - 100 < mouse_x < WIDTH // 2 + 100) and (HEIGHT // 2 - 30 < mouse_y < HEIGHT // 2 + 30):
                    regist()

        screen.fill((0, 0, 0))
        draw_map(screen, begin, camera_x, camera_y)
        draw_button(screen, "Старт", WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 60)

        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()


def create_collision_objects(tmx_data, scale_factor):
    collision_objects = []
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Collision":
            for obj in layer:
                obj_rect = pygame.Rect(obj.x * scale_factor, obj.y * scale_factor,
                                       obj.width * scale_factor, obj.height * scale_factor)
                collision_objects.append(obj_rect)
    return collision_objects


def check_collisions(player_rect, collision_objects):
    for obj in collision_objects:
        if player_rect.colliderect(obj):
            return True
    return False


def move_player(player_rect, keys, map_width, map_height):
    original_rect = player_rect.copy()
    if keys[pygame.K_LEFT]:
        original_rect.x -= 5
    if keys[pygame.K_RIGHT]:
        original_rect.x += 5
    if keys[pygame.K_UP]:
        original_rect.y -= 5
    if keys[pygame.K_DOWN]:
        original_rect.y += 5
    original_rect.x = max(0, min(original_rect.x, map_width - player_rect.width))
    original_rect.y = max(0, min(original_rect.y, map_height - player_rect.height))
    return original_rect


def update_camera(player_rect, screen_width, screen_height, map_width, map_height):
    camera_x = player_rect.centerx - screen_width // 2
    camera_y = player_rect.centery - screen_height // 2
    camera_x = max(0, min(camera_x, map_width - screen_width))
    camera_y = max(0, min(camera_y, map_height - screen_height))
    return camera_x, camera_y


def drawmap(screen, tmx_data, camera_x, camera_y, scale_factor):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    tile = pygame.transform.scale(tile,
                                                  (tile.get_width() * scale_factor, tile.get_height() * scale_factor))
                    screen.blit(tile, (x * tmx_data.tilewidth * scale_factor - camera_x,
                                       y * tmx_data.tileheight * scale_factor - camera_y))


def init_game():
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("")
    return screen, screen_width, screen_height


def game(volume, brightness, user_login):
    screen, screen_width, screen_height = init_game()
    tmx_data = load_map('map/уровень первый тот первый по ошибке.tmx')
    pygame.mixer.music.set_volume(volume)
    player_image = load_image('z1.png')
    player_rect = player_image.get_rect()
    player_rect.topleft = (400, 350)

    scale_factor = 2
    map_width = tmx_data.width * tmx_data.tilewidth * scale_factor
    map_height = tmx_data.height * tmx_data.tileheight * scale_factor

    collision_objects = create_collision_objects(tmx_data, scale_factor)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        original_rect = move_player(player_rect, keys, map_width, map_height)

        if not check_collisions(original_rect, collision_objects):
            player_rect = original_rect

        camera_x, camera_y = update_camera(player_rect, screen_width, screen_height, map_width, map_height)

        screen.fill((0, 0, 0))
        drawmap(screen, tmx_data, camera_x, camera_y, scale_factor)
        screen.blit(player_image, (player_rect.x - camera_x, player_rect.y - camera_y))

        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()



play_music()
main()
terminate()
