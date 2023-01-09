import pygame
from support import import_csv_layout, import_cut_graphics
from tiles import StaticTile, Crate, Palm, Coin
from decoration import Sky, Water, Clouds
from player import Player
import random


class Level:
    def __init__(self, level_data, surface, change_score):
        self.display_surface = surface

        # игрок
        player_layout = import_csv_layout(level_data["player"])
        self.player = pygame.sprite.GroupSingle()
        self.create_player(player_layout)
        self.current_x = 0

        # звуки
        self.coin_sound = pygame.mixer.Sound("data/effects/coin.wav")

        # интерфейс
        self.change_score = change_score

        # ландшафт
        terrain_layout = import_csv_layout(level_data["terrain"])
        self.terrain_sprites = self.create_tile_group(terrain_layout, "terrain")

        # монеты
        coin_layout = import_csv_layout(level_data["coins"])
        self.coin_sprites = self.create_tile_group(coin_layout, "coins")
        # трава
        grass_layout = import_csv_layout(level_data["grass"])
        self.grass_sprites = self.create_tile_group(grass_layout, "grass")

        # ящики
        crates_layout = import_csv_layout(level_data["crates"])
        self.crates_sprites = self.create_tile_group(crates_layout, "crates")

        # пальмы на переднем плане
        fg_palm_layout = import_csv_layout(level_data["fg palms"])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout, "fg palms")

        # пальмы на заднем плане
        bg_palm_layout = import_csv_layout(level_data["bg palms"])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout, "bg palms")

        # декорации
        self.sky = Sky(6)
        self.water = Water(680, 1280)
        self.clouds = Clouds(375, 1280, 20)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                #  если значение -1, то там ничего нет
                if val != "-1":
                    # 64 - это размер клеточек, на которые поделена карта моей игры
                    x = col_index * 64
                    y = row_index * 64
                    # создаём спрайты наших тайлов в зависимости от их типа
                    if type == "terrain":
                        terrain_tile_list = import_cut_graphics("graphics/terrain/terrain_tiles.png")
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(64, x, y, tile_surface)

                    if type == "grass":
                        grass_tile_list = import_cut_graphics("graphics/decoration/grass/grass.png")
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(64, x, y, tile_surface)

                    if type == "crates":
                        sprite = Crate(64, x, y)

                    if type == "fg palms":
                        if val == "0":
                            sprite = Palm(64, x, y, "graphics/terrain/palm_small", 38)
                        if val == "1":
                            sprite = Palm(64, x, y, "graphics/terrain/palm_large", 64)

                    if type == "bg palms":
                        sprite = Palm(64, x, y, "graphics/terrain/palm_bg", 64)

                    if type == "coins":
                        if val == "0":
                            sprite = Coin(64, x, y, "graphics/coins/gold", 5)
                        if val == "1":
                            sprite = Coin(64, x, y, "graphics/coins/silver", 1)
                    sprite_group.add(sprite)
        return sprite_group

    def create_player(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * 64
                y = row_index * 64
                if val == "0":
                    sprite = Player((x, y))
                    self.player.add(sprite)

    def horizontal_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right
        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_top = True
                elif player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_top and player.direction.y > 0:
            player.on_top = False

    def coin_collision(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            self.coin_sound.play()
            self.coin_sound.set_volume(0.1)
            for coin in collided_coins:
                self.change_score(coin.value)

    def coin_vertical_collision(self):
        coins = self.coin_sprites.sprites()
        for coin in coins:
            coin.apply_gravity()
            for sprite in self.terrain_sprites.sprites():
                if sprite.rect.colliderect(coin.rect):
                    if coin.direction.y < 0:
                        coin.rect.top = sprite.rect.bottom
                        coin.direction.y = 0
                    elif coin.direction.y > 0:
                        coin.rect.bottom = sprite.rect.top
                        coin.direction.y = 0

    def coin_spawn(self):
        spawn_place = random.randint(32, 1258)
        offset = 64
        # условие, чтобы монеты не падали в воду
        if 820 < spawn_place < 910:
            spawn_place += offset
            offset = -offset
        sprite = Coin(64, spawn_place, -32, "graphics/coins/gold", 5)
        self.coin_sprites.add(sprite)

    # запуск игры
    def run(self):
        # отрисовка спрайтов
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface)

        self.bg_palm_sprites.update()
        self.bg_palm_sprites.draw(self.display_surface)

        self.terrain_sprites.draw(self.display_surface)
        self.crates_sprites.draw(self.display_surface)
        self.grass_sprites.draw(self.display_surface)

        self.coin_sprites.draw(self.display_surface)
        self.coin_sprites.update()

        self.fg_palm_sprites.update()
        self.fg_palm_sprites.draw(self.display_surface)

        self.player.update()
        self.horizontal_collision()
        self.vertical_collision()
        self.player.draw(self.display_surface)

        self.water.draw(self.display_surface)

        self.coin_collision()
        self.coin_vertical_collision()
