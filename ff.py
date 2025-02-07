import os
import sqlite3
import sys
import pygame
import pytmx
import screen_brightness_control as sbc

pygame.init()
size = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


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
    load_image('o1.png'),
    load_image('z1.png')
]

animation_frames = {
    0: [load_image('z2.png'), load_image('z3.png'), load_image('z4.png'), load_image('z5.png')],
    1: [load_image('ch2.jpg'), load_image('ch3.jpg')],
    2: [load_image('l2.png'), load_image('l3.png'), load_image('l4.png'), load_image('l5.png')],
    3: [load_image('o2.png'), load_image('o3.png')]
}

current_index = 0
current_frame = 0
animation_speed = 5
frame_counter = 0


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
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    volume, brightness = load_settings(user_login)
    pygame.mixer.music.set_volume(volume)
    sbc.set_brightness(int(brightness * 100))

    def handle_events():
        global volume, brightness
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_settings(volume, brightness, user_login)
                    print(user_login)
                    return True  # Указываем, что нужно выйти из цикла

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if 50 < mouse_x < 550:
                        if 150 < mouse_y < 180:
                            volume = (mouse_x - 50) / 500
                            pygame.mixer.music.set_volume(volume)
                        elif 250 < mouse_y < 280:
                            brightness = (mouse_x - 50) / 500
                            sbc.set_brightness(int(brightness * 100))
        return False

    while True:
        if handle_events():
            break

        screen.fill((int(200 * brightness), int(200 * brightness), int(200 * brightness)))
        pygame.draw.rect(screen, (255, 255, 255), (50, 150, 500, 30))
        pygame.draw.rect(screen, (255, 255, 255), (50, 250, 500, 30))
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

        if button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            conn = sqlite3.connect('Escape.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM регистрация WHERE Логин = ?', (user_login,))
            result = cursor.fetchone()

            if result:
                user_id = result[0]
                cursor.execute('SELECT character_id FROM персонажи WHERE user_id = ?', (user_id,))
                existing_character = cursor.fetchone()
                character_id = existing_character[0] if existing_character else 1
            else:
                character_id = 1

            save_settings(volume, brightness, user_login)
            startgame(volume, brightness, user_login, character_id)

        pygame.display.flip()
        clock.tick(60)


def save_to_db(user_texts):
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO регистрация (Имя, Логин, пароль) VALUES (?, ?, ?)''',
                   (user_texts[0], user_texts[1], user_texts[2]))
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id


def terminate():
    pygame.quit()
    sys.exit()


def load_character_from_db(user_login):
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM регистрация WHERE Логин = ?', (user_login,))
    result = cursor.fetchone()
    user_id = result[0]
    cursor.execute('SELECT character_id FROM персонажи WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def change_character(direction):
    global current_index, current_frame
    current_index = (current_index + direction) % len(characters)
    current_frame = 0


def save_character_to_db(user_login, character_id):
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM регистрация WHERE Логин = ?', (user_login,))
    result = cursor.fetchone()

    if result:
        user_id = result[0]
        cursor.execute('SELECT character_id FROM персонажи WHERE user_id = ?', (user_id,))
        existing_character = cursor.fetchone()

        if existing_character:
            cursor.execute('UPDATE персонажи SET character_id = ? WHERE user_id = ?', (character_id, user_id))
        else:
            print(user_id)
            print(character_id)
            cursor.execute('INSERT INTO персонажи (user_id, character_id) VALUES (?, ?)', (user_id, character_id))

        conn.commit()
    conn.close()


def draw_characters(window, user_login, volume, brightness):
    global current_frame, frame_counter
    window.fill((255, 255, 255))

    # Update frame counter for animation
    frame_counter += 1
    if frame_counter >= animation_speed:  # Adjust animation speed here
        current_frame = (current_frame + 1) % len(animation_frames[current_index])
        frame_counter = 0

    scale_factor = 4
    left_index = (current_index - 1) % len(characters)
    right_index = (current_index + 1) % len(characters)

    # Load and scale images for left, center, and right characters
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

    # Set positions for the characters
    left_pos = (WIDTH // 3 - 150 - left_image.get_width() // 2, HEIGHT // 2 - 100)
    center_pos = (WIDTH // 2 + 40 - center_image.get_width() // 2, HEIGHT // 2 - 250)
    right_pos = (2 * WIDTH // 3 + 200 - right_image.get_width() // 2, HEIGHT // 2 - 100)

    # Draw characters on the window
    window.blit(left_image, left_pos)
    window.blit(center_image, center_pos)
    window.blit(right_image, right_pos)

    # Save button
    save_button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 100, 150, 75)
    pygame.draw.rect(window, (200, 200, 200), save_button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render('Выбрать', True, (0, 0, 0))
    window.blit(text, (save_button_rect.x + 35, save_button_rect.y + 35))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левый клик мыши
                if save_button_rect.collidepoint(event.pos):
                    save_character_to_db(user_login, current_index)
                    startgame(volume, brightness, user_login, current_index)
                    return


def open_new_window(user_login, volume, brightness):
    new_window_size = (1280, 720)
    new_window = pygame.display.set_mode(new_window_size)
    pygame.display.set_caption("Персонажи")

    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM регистрация WHERE Логин = ?', (user_login,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            cursor.execute('SELECT volume, brightness FROM settings WHERE id_user = ?', (user_id,))
            existing_character = cursor.fetchone()
            volume = existing_character[0] if existing_character else 0.5
            brightness = existing_character[1] if existing_character else 0.5
        else:
            volume, brightness = 0.5, 0.5

        selected_character_id = load_character_from_db(user_login)
        if selected_character_id is not None:
            global current_index
            current_index = selected_character_id

        # Установим начальное состояние для обновления
        needs_redraw = True

        while True:
            if needs_redraw:
                draw_characters(new_window, user_login, volume, brightness)
                needs_redraw = False  # Сброс флага после отрисовки

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if mouse_x < WIDTH // 4:  # Увеличиваем область для левого клика
                        change_character(-1)
                        needs_redraw = True  # Персонаж изменился, нужно перерисовать
                    elif mouse_x > 3 * WIDTH // 4:  # Увеличиваем область для правого клика
                        change_character(1)
                        needs_redraw = True  # Персонаж изменился, нужно перерисовать
                    elif event.button == 1:  # Левый клик мыши
                        save_character_to_db(user_login, current_index)  # Сохранить выбранного персонажа
                        startgame(volume, brightness, user_login, current_index)  # Начать игру с выбранным персонажем

            pygame.display.flip()
            clock.tick(30)  # Уменьшение частоты обновления до 30 кадров в секунду
    except sqlite3.Error as e:
        print("Database error:", e)
    finally:
        conn.close()


def startgame(volume, brightness, user_login, character_id):
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
                        game(volume, brightness, user_login)
                        return
                    elif button2_rect.collidepoint(mouse_pos):
                        settings_window(user_login)
                        return
                    elif button3_rect.collidepoint(mouse_pos):
                        open_new_window(user_login, volume, brightness)
                        return

        pygame.display.flip()
        clock.tick(60)


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
                    character_id = 1
                    save_to_db(user_texts)
                    startgame(volume, brightness, user_login, character_id)
                    return
                if buttonpast.collidepoint(event.pos):
                    main()
                    return
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


def draw_map(screen, tmx_data, camera_x, camera_y):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth + camera_x, y * tmx_data.tileheight + camera_y))


def draw_button(screen, text, x, y, width, height):
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height))
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)
    return


def center_camera(screen_width, screen_height, map_width, map_height):
    camera_x = (screen_width - map_width) // 2
    camera_y = (screen_height - map_height) // 2
    return camera_x, camera_y


def load_map(filename):
    return pytmx.load_pygame(filename)


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
                    return

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


def create_level_objects(tmx_data, scale_factor):
    level_objects = []
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "уровень":
            for obj in layer:
                obj_rect = pygame.Rect(obj.x * scale_factor, obj.y * scale_factor,
                                       obj.width * scale_factor, obj.height * scale_factor)
                level_objects.append(obj_rect)
    return level_objects


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


# Функция для загрузки объектов из карты
def load_map_objects(tmx_data):
    objects = {}
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledObjectGroup) and layer.name in ['красный', 'синий', 'розовый', 'жёлтый']:
            objects[layer.name] = [obj for obj in layer]
    return objects

# Функция для сохранения счета в БД
def save_score(user_login, score):
    conn = sqlite3.connect('Escape.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scores (user_login, score) VALUES (?, ?)', (user_login, score))
    conn.commit()
    conn.close()

# Глобальные переменные для соединения объектов
objects_to_connect = []
connected_pairs = []

# Функция для соединения объектов
def connect_objects(object1, object2):
    if (object1, object2) not in connected_pairs and (object2, object1) not in connected_pairs:
        connected_pairs.append((object1, object2))
        print(f'Соединены объекты: {object1} и {object2}')
        draw_connection(object1, object2)  # Визуализация соединения

# Функция для проверки, соединены ли все пары
def all_pairs_connected():
    total_pairs = len(objects_to_connect) // 2
    return len(connected_pairs) == total_pairs

# Функция для проверки соединения и обновления счета
def check_connection_and_update_score(user_login, timer_start):
    score = 0
    if all_pairs_connected():
        elapsed_time = pygame.time.get_ticks() - timer_start
        if elapsed_time <= 15000:
            score += 5
        elif elapsed_time <= 30000:
            score += 2
        elif elapsed_time <= 60000:
            score += 1

        if elapsed_time < 60000:
            score += 1

        save_score(user_login, score)

# Функция для обработки клика на объект
def on_object_click(object):
    if object not in objects_to_connect:
        objects_to_connect.append(object)
    if len(objects_to_connect) == 2:
        connect_objects(objects_to_connect[0], objects_to_connect[1])
        objects_to_connect.clear()

# Функция для рисования линии между двумя объектами
def draw_connection(object1, object2):
    pygame.draw.line(screen, (255, 0, 0), (object1.x, object1.y), (object2.x, object2.y), 5)


def game(volume, brightness, user_login):
    screen, screen_width, screen_height = init_game()
    tmx_data = load_map('map/уровень первый тот первый по ошибке.tmx')
    pygame.mixer.music.set_volume(volume)

    # Загрузка персонажа игрока на основе ID из базы данных
    character_id = load_character_from_db(user_login)
    player_image = load_character_image(character_id)
    player_rect = player_image.get_rect()
    player_rect.topleft = (400, 350)

    scale_factor = 2
    map_width = tmx_data.width * tmx_data.tilewidth * scale_factor
    map_height = tmx_data.height * tmx_data.tileheight * scale_factor
    collision_objects = create_collision_objects(tmx_data, scale_factor)
    level_objects = create_level_objects(tmx_data, scale_factor)

    timer_start = pygame.time.get_ticks()
    timer_duration = 20000  # 20 секунд
    allan_image_frames = load_allan_images()
    allan_rect = player_rect.copy()  # Аллан появляется в том же месте, что и игрок
    allan_animation_index = 0
    allan_speed = 3  # Скорость Аллана
    allan_spawned = False
    show_screamer = False
    screamer_image = load_image('скример.jpg')
    screamer_display_time = 5000
    screamer_start_time = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
                if (400 <= event.pos[0] <= 590) and (540 <= event.pos[1] <= 590):
                    print('загрузка')
                    player_rect = None  # Скрываем игрока
                    allan_rect = None
                    screen, screen_width, screen_height = init_game()
                    tmx_data = load_map('map/vbyb buhf.tmx')
                    print('lll')
                    # Обновление экрана после загрузки карты
                    screen.fill((0, 0, 0))
                     # Функция для отрисовки карты
                    pygame.display.flip()
                    # Отладочное сообщение
        # ... существующий код ...

        keys = pygame.key.get_pressed()
        original_rect = move_player(player_rect, keys, map_width, map_height)
        if not check_collisions(original_rect, collision_objects):
            player_rect = original_rect

        camera_x, camera_y = update_camera(player_rect, screen_width, screen_height, map_width, map_height)

        elapsed_time = pygame.time.get_ticks() - timer_start
        if elapsed_time >= timer_duration and not allan_spawned:
            allan_spawned = True  # Аллан появляется через 20 секунд
            allan_rect.topleft = (400, 350)  # Начальная позиция Аллана

        if allan_spawned:
            # Обновление позиции Аллана
            if allan_rect.x < player_rect.x:
                new_rect = allan_rect.move(allan_speed, 0)
                if not check_collisions(new_rect, collision_objects):
                    allan_rect.x += allan_speed
            elif allan_rect.x > player_rect.x:
                new_rect = allan_rect.move(-allan_speed, 0)
                if not check_collisions(new_rect, collision_objects):
                    allan_rect.x -= allan_speed

            if allan_rect.y < player_rect.y:
                new_rect = allan_rect.move(0, allan_speed)
                if not check_collisions(new_rect, collision_objects):
                    allan_rect.y += allan_speed
            elif allan_rect.y > player_rect.y:
                new_rect = allan_rect.move(0, -allan_speed)
                if not check_collisions(new_rect, collision_objects):
                    allan_rect.y -= allan_speed

            # Проверка на столкновение между игроком и Алланом
            if player_rect.colliderect(allan_rect):
                show_screamer = True
                screamer_start_time = pygame.time.get_ticks()

        # Отрисовка
        screen.fill((0, 0, 0))
        drawmap(screen, tmx_data, camera_x, camera_y, scale_factor)
        screen.blit(player_image, (player_rect.x - camera_x, player_rect.y - camera_y))

        # Отрисовка Аллана, если он появился
        if allan_spawned:
            allan_image = allan_image_frames[allan_animation_index]
            screen.blit(allan_image, (allan_rect.x - camera_x, allan_rect.y - camera_y))
            allan_animation_index = (allan_animation_index + 1) % len(allan_image_frames)

        # Отрисовка таймера
        timer_text = f'Time: {elapsed_time // 1000}'
        font = pygame.font.Font(None, 36)
        timer_surface = font.render(timer_text, True, (255, 255, 255))
        screen.blit(timer_surface, (10, 10))

        # Отображение скримера, если необходимо
        if show_screamer:
            screamer_surface = pygame.transform.scale(screamer_image, (1280, 720))
            screen.blit(screamer_surface, (0, 0))
            if pygame.time.get_ticks() - screamer_start_time >= screamer_display_time:
                startgame(volume, brightness, user_login,
                          character_id)  # Запуск функции gamestart после показа скримера

        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()


def forest(volume, brightness, user_login):
    # Логика функции forest, аналогичная функции game, но с другой картой
    pass


def load_character_image(character_id):
    # Function to load character image based on ID
    character_images = {
        0: load_image('z1.png'),
        1: load_image('ch1.jpg'),
        2: load_image('l1.jpg'),
        3: load_image('o1.png'),
    }
    return character_images.get(character_id, load_image('z1.png'))  # Default image if ID not found


def load_allan_images():
    # Function to load Allan's images
    return [load_image(f'аллан{i}.png') for i in range(1, 6)]


def load_allan_character():
    # Function to initialize Allan's position
    return pygame.Rect(100, 100, 50, 50)  # Example position and size


if __name__ == "__main__":
    play_music()
    main()
    terminate()
