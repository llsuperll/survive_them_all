from csv import reader
import pygame
from os import walk


# функция помогает импортировать сразу все изображения из нужной папки
def import_folder(path):
    surface_list = []
    # первые 2 значения нам не нужны, т.к. это адрес каталога (папки)
    # и список подкаталогов (вложенных папок)
    for _, __, image_files in walk(path):
        for image_file in image_files:
            full_path = path + "/" + image_file
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)
    return surface_list


# функция конвертирует информацию из csv файла в список
def import_csv_layout(path):
    terrain_map = []
    with open(path) as f:
        level = reader(f, delimiter=",")
        for row in level:
            terrain_map.append(list(row))
        # каждый row это ряд квадратиков в игре, у него есть значение, которое определяет картинку
        return terrain_map


# импорт листа тайлов с помощью разбиения его на части (сами тайлы)
def import_cut_graphics(path):
    # convert_alpha() для изображений с прозрачным фоном
    surface = pygame.image.load(path).convert_alpha()
    # узнаем сколько тайлов в нашем тайлсете
    tile_num_x = surface.get_width() // 64
    tile_num_y = surface.get_height() // 64

    cut_tiles = []
    # перебираем тайлы и создаём новую поверхность уже с картинкой
    # это делаем, чтобы затем нанести эту поверхность на нужный тайл в самой игре
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * 64
            y = row * 64
            new_surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
            # альфа канал для каждого пикселя, грубо говоря, теперь это пнг картинка в питоне
            new_surface.blit(surface, (0, 0), pygame.Rect(x, y, 64, 64))
            cut_tiles.append(new_surface)
    return cut_tiles
