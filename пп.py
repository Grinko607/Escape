import pygame
import pytmx

def draw_map(screen, tmx_data):
    for layer in tmx_data.visible_layers:  # Итерируем по видимым слоям
        if isinstance(layer, pytmx.TiledTileLayer):  # Проверяем, что это тайловый слой
            for x, y, gid in layer:  # Распаковываем координаты и gid
                tile = tmx_data.get_tile_image_by_gid(gid)  # Получаем изображение тайла
                if tile:  # Проверяем, что изображение существует
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))  # Рисуем тайл
        elif isinstance(layer, pytmx.TiledObjectGroup):  # Проверяем, что это группа объектов
            for obj in layer:  # Итерируем по объектам в группе
                if obj.image:  # Проверяем, что у объекта есть изображение
                    screen.blit(obj.image, (obj.x, obj.y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    tmx_data = pytmx.load_pygame("map/sandbox2.tmx")  # Замените на путь к Вашей карте
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill((0, 0, 0))  # Очищаем экран
        draw_map(screen, tmx_data)  # Рисуем карту
        pygame.display.flip()  # Обновляем экран
        clock.tick(60)  # Ограничиваем FPS

if __name__ == "__main__":
    main()
