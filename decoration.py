import pygame
from tiles import AnimatedTile, StaticTile
from support import import_folder
from random import choice, randint


# класс неба
class Sky:
    def __init__(self, horizon):
        self.top = pygame.image.load("graphics/decoration/sky/sky_top.png").convert()
        self.bottom = pygame.image.load("graphics/decoration/sky/sky_bottom.png").convert()
        self.middle = pygame.image.load("graphics/decoration/sky/sky_middle.png").convert()
        self.horizon = horizon

        # сразу задаем размер во всю ширину экрана, чтобы не рисовать по тайлам
        self.top = pygame.transform.scale(self.top, (1280, 64))
        self.bottom = pygame.transform.scale(self.bottom, (1280, 64))
        self.middle = pygame.transform.scale(self.middle, (1280, 64))

    def draw(self, surface):
        # у неба есть горизонт поэтому его изображения отличаются на разных уровнях
        for row in range(12):
            y = row * 64
            if row < self.horizon:
                surface.blit(self.top, (0, y))
            elif row == self.horizon:
                surface.blit(self.middle, (0, y))
            else:
                surface.blit(self.bottom, (0, y))


# класс воды
class Water:
    def __init__(self, top, level_width):
        water_start = 0
        water_tile_width = 192
        tile_x_amount = int(level_width / water_tile_width) + 1
        self.water_sprites = pygame.sprite.Group()

        for tile in range(tile_x_amount):
            x = tile * water_tile_width + water_start
            y = top
            sprite = AnimatedTile(192, x, y, "graphics/decoration/water")
            self.water_sprites.add(sprite)

    def draw(self, surface):
        self.water_sprites.update()
        self.water_sprites.draw(surface)


# класс облаков
class Clouds:
    def __init__(self, horizon, level_width, cloud_number):
        cloud_surface_list = import_folder("graphics/decoration/clouds")
        min_x = 0
        max_x = level_width
        min_y = 0
        max_y = horizon
        self.cloud_sprites = pygame.sprite.Group()

        # создаём облака в рандомных местах
        for cloud in range(cloud_number):
            cloud = choice(cloud_surface_list)
            x = randint(min_x, max_x)
            y = randint(min_y, max_y)
            sprite = StaticTile(0, x, y, cloud)
            self.cloud_sprites.add(sprite)

    def draw(self, surface):
        self.cloud_sprites.update()
        self.cloud_sprites.draw(surface)
