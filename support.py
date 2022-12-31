from csv import reader
import pygame
from os import walk


def import_folder(path):
    surface_list = []

    for _, __, image_files in walk(path):
        for image_file in image_files:
            full_path = path + "/" + image_file
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)
    return surface_list


def import_csv_layout(path):
    terrain_map = []
    with open(path) as f:
        level = reader(f, delimiter=",")
        for row in level:
            terrain_map.append(list(row))
        return terrain_map


def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = surface.get_width() // 64
    tile_num_y = surface.get_height() // 64

    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * 64
            y = row * 64
            new_surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
            new_surface.blit(surface, (0, 0), pygame.Rect(x, y, 64, 64))
            cut_tiles.append(new_surface)
    return cut_tiles
