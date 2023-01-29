import pygame
from support import import_csv_layout, import_cut_graphics
from tiles import StaticTile, Crate, Palm, Coin
from decoration import Sky, Water, Clouds
from player import Player, Enemy, ParticleEffect, Boss
import random


class Level:
    def __init__(self, level_data, surface, change_score, change_health):
        self.display_surface = surface

        # игрок
        player_layout = import_csv_layout(level_data["player"])
        self.player = pygame.sprite.GroupSingle()
        self.create_player(player_layout, change_health)
        self.current_x = 0
        self.win_game = False

        # враги
        self.enemies = pygame.sprite.Group()
        self.explosion_particle = pygame.sprite.Group()
        self.wave_number = 0
        self.priority = False

        # звуки
        self.coin_sound = pygame.mixer.Sound("data/effects/coin.wav")
        self.enemy_explosion_sound = pygame.mixer.Sound("data/effects/stomp.wav")
        self.fight_music = pygame.mixer.Sound("data/fight_music.wav")

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

    # создание групп тайлов
    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                #  если значение -1, то там ничего нет
                if val != "-1":
                    # 64 - это размер клеточек, на которые поделена карта игры
                    x = col_index * 64
                    y = row_index * 64
                    # создаём спрайты тайлов в зависимости от их типа
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

    # создание спрайта игрока
    def create_player(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * 64
                y = row_index * 64
                if val == "0":
                    sprite = Player((x, y), change_health)
                    self.player.add(sprite)

    # создание спрайтов врагов
    def create_enemy(self):
        spawn_place = [(random.randint(-400, -10), 400), (random.randint(1290, 1590), 400)]
        enemy = Enemy(random.choice(spawn_place))
        self.enemies.add(enemy)

    # создание спрайтов боссов
    def spawn_boss(self):
        spawn_place = [(random.randint(-400, -10), 440), (random.randint(1290, 1590), 440)]
        boss1 = Boss(random.choice(spawn_place), "spirit")
        boss2 = Boss(spawn_place[0], "bamboo")
        boss3 = Boss(random.choice(spawn_place), "squid")
        self.enemies.add(boss1, boss2, boss3)

    # преследование игрока
    def chasing(self):
        for enemy in self.enemies:
            enemy.chase_player(self.player)
            # добавление прыжка врагам в нужных местах
            if 910 < enemy.rect.x < 940:
                enemy.jump()
            if 800 < enemy.rect.x < 810:
                enemy.jump()
            if 0 < enemy.rect.x < 1280 and self.player.sprite.rect.y < 320 and enemy.rect.y <= 450 and \
                    abs(self.player.sprite.rect.x - enemy.rect.x) < 300:
                enemy.jump()

    # обработка горизонтальных столкновений для игрока
    def horizontal_collision(self):
        player = self.player.sprite
        # движение по экрану
        player.rect.x += player.direction.x * player.speed
        # перебираем спрайты поверхности
        for sprite in self.terrain_sprites.sprites():
            # если игрок касается спрайта поверхности по горизонтали, то координата игрока в точке столкновения
            # (правая или левая) будет равняться координате объекта поверхности в точке касания
            # переменные on_left, on_right введены для определения стороны точки касания
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

    # обработка горизонтальных столкновений для врагов
    def enemy_horizontal_collision(self):
        for enemy in self.enemies:
            enemy.rect.x += enemy.direction.x * enemy.speed

        for sprite in self.terrain_sprites.sprites():
            for enemy in self.enemies:
                if sprite.rect.colliderect(enemy.rect):
                    if enemy.direction.x < 0:
                        enemy.rect.left = sprite.rect.right
                        enemy.jump()
                    elif enemy.direction.x > 0:
                        enemy.rect.right = sprite.rect.left
                        enemy.jump()

    # обработка вертикальных столкновений для игрока
    def vertical_collision(self):
        player = self.player.sprite
        # гравитация
        player.apply_gravity()
        # ограничение карты в верхней точке
        if player.rect.top < -32:
            player.rect.top = -32
            player.direction.y = 0
        # работает аналогично методу горизонтальных столкновений для поверхностей сверху и снизу от игрока
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

    # обработка горизонтальных столкновений для врагов
    def enemy_vertical_collision(self):
        for enemy in self.enemies:
            # для огонька добавляем возможность перемещения по оси y
            if enemy.enemy_type == "Boss" and enemy.gravity_immune:
                enemy.rect.y += enemy.direction.y * enemy.speed
            enemy.apply_gravity()
            for sprite in self.terrain_sprites.sprites():
                if sprite.rect.colliderect(enemy.rect):
                    if enemy.direction.y < 0:
                        enemy.rect.top = sprite.rect.bottom
                        enemy.direction.y = 0
                    elif enemy.direction.y > 0:
                        enemy.rect.bottom = sprite.rect.top
                        enemy.direction.y = 0
                        enemy.on_ground = True

            if enemy.on_ground and enemy.direction.y < 0 or enemy.direction.y > 1:
                enemy.on_ground = False

    # обработка столкновений игрока с врагами
    def collision_player_enemy(self):
        collided_enemy = pygame.sprite.spritecollide(self.player.sprite, self.enemies, False)

        if collided_enemy:
            enemy_died = False
            for enemy in collided_enemy:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                no_damage = False
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    # игрок подпрыгивает
                    self.player.sprite.direction.y = -19
                    no_damage = True
                    if enemy.enemy_type == "Boss":
                        # способности боссов
                        if enemy.boss_type == "spirit":
                            enemy.rect.x += random.choice([120, -120])
                            enemy.rect.y += 32
                        elif enemy.boss_type == "bamboo":
                            enemy.enemy_status = "attack"
                            self.player.sprite.change_health(-5)
                    explosion_sprite = ParticleEffect(enemy.rect.center, "enemy death")
                    self.explosion_particle.add(explosion_sprite)
                    self.enemy_explosion_sound.play()
                    enemy.health -= 50
                    if enemy.health <= 0:
                        enemy.kill()
                        if enemy.enemy_type == "Boss":
                            for i in range(5):
                                self.coin_spawn(enemy.rect)
                        else:
                            self.coin_spawn(enemy.rect)
                        enemy_died = True
                else:
                    if not enemy_died:
                        if enemy.enemy_type == "Boss":
                            enemy.enemy_status = "attack"
                            if not no_damage:
                                self.player.sprite.get_damage(-15)
                        else:
                            # от обычных врагов
                            self.player.sprite.get_damage(-5)

    # спавн врагов
    def spawn_enemies(self, wave):
        multiplier = 1.2
        for i in range(int((wave + 5) * multiplier)):
            self.create_enemy()

    # реализация волн врагов в игре
    def waves_management(self):
        if self.wave_number == 0:
            if not self.coin_sprites:
                self.wave_number += 1
                self.spawn_enemies(self.wave_number)
                pygame.mixer.stop()
                self.fight_music.play(loops=-1)
        elif not self.enemies and self.wave_number == 7:
            self.player.sprite.get_health(150)
            self.spawn_boss()
            self.wave_number += 1
            self.priority = True
        elif not self.enemies and not self.priority:
            self.spawn_enemies(self.wave_number)
            self.wave_number += 1
        if self.priority and not self.enemies:
            if not self.coin_sprites:
                self.win_game = True

    # если кто-то падает в воду, то он умирает
    def check_position(self):
        if self.player.sprite.rect.bottom >= 780:
            self.player.sprite.get_damage(-100)
        for enemy in self.enemies:
            if enemy.rect.bottom >= 780:
                enemy.kill()
        for coin in self.coin_sprites:
            if coin.rect.bottom >= 780:
                coin.kill()

    # обработка столкновения игрока и монеты
    def coin_collision(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            self.coin_sound.play()
            self.coin_sound.set_volume(0.1)
            for coin in collided_coins:
                self.change_score(coin.value)

    # гравитация монет
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

    # спавн монет
    def coin_spawn(self, pos):
        spawn_place = pos
        rnd = [i for i in range(1, 11)]
        # рандомный выбор золотой или серебряной монеты
        num = random.choice(rnd)
        flag = False
        if num < 3:
            sprite = Coin(64, spawn_place[0], spawn_place[1], "graphics/coins/gold", 5)
            flag = True
        elif 3 < num < 8:
            sprite = Coin(64, spawn_place[0], spawn_place[1], "graphics/coins/silver", 1)
            flag = True
        if flag:
            self.coin_sprites.add(sprite)
            sprite.coin_jump()

    # запуск игры
    def run(self):
        # отрисовка и обновление спрайтов
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

        # игрок
        self.player.update()
        self.horizontal_collision()
        self.vertical_collision()
        self.player.draw(self.display_surface)
        self.check_position()

        # враги
        self.enemies.update()
        self.chasing()
        self.enemies.draw(self.display_surface)
        self.enemy_horizontal_collision()
        self.enemy_vertical_collision()
        self.collision_player_enemy()
        self.explosion_particle.update()
        self.explosion_particle.draw(self.display_surface)
        self.waves_management()

        self.water.draw(self.display_surface)

        self.coin_collision()
        self.coin_vertical_collision()
