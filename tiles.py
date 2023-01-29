import random
import pygame
from support import import_folder


# базовый класс для всех тайлов
class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x, y))


# класс для статичных тайлов
class StaticTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface


# класс ящика
class Crate(StaticTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, pygame.image.load("graphics/terrain/crate.png").convert_alpha())
        offset_y = y + size
        # устанавливаем оффсет, чтобы ящик не летал в воздухе
        self.rect = self.image.get_rect(bottomleft=(x, offset_y))


# класс анимированного тайла
class AnimatedTile(Tile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    # функция, отвечающая за анимацию
    def animate(self):
        self.frame_index += 0.15
        # если индекс превысит кол-во всех изображений, то будет обнулён
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()


# класс пальмы
class Palm(AnimatedTile):
    def __init__(self, size, x, y, path, offset):
        super().__init__(size, x, y, path)
        offset_y = y - offset
        # оффсет пальме нужен по той же причине, что и ящику,
        # только здесь немного другая ситуация
        self.rect.topleft = (x, offset_y)


# класс монеты
class Coin(AnimatedTile):
    def __init__(self, size, x, y, path, value):
        super().__init__(size, x, y, path)
        self.rect = self.image.get_rect(center=(x + int(size / 2), y + int(size / 2)))
        self.value = value
        self.direction = pygame.math.Vector2(0, 0)
        self.gravity = 0.8

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    # эффект вылетания монеты из врага
    def coin_jump(self):
        x = [64, -64]
        self.rect.x += random.choice(x)
        self.rect.y += 64
