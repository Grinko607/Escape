import os
import sys
import pygame
import pytmx

def init_game():
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Перемещение по карте Tiled")
    return screen, screen_width, screen_height

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

def draw_map(screen, tmx_data, camera_x, camera_y, scale_factor):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    tile = pygame.transform.scale(tile,
                                                  (tile.get_width() * scale_factor, tile.get_height() * scale_factor))
                    screen.blit(tile, (x * tmx_data.tilewidth * scale_factor - camera_x,
                                       y * tmx_data.tileheight * scale_factor - camera_y))

def game():
    screen, screen_width, screen_height = init_game()
    tmx_data = load_map('map/уровень первый тот первый по ошибке.tmx')

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
        draw_map(screen, tmx_data, camera_x, camera_y, scale_factor)
        screen.blit(player_image, (player_rect.x - camera_x, player_rect.y - camera_y))

        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()



