import pygame
from support import import_folder
from math import sin
import random


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, change_health):
        super().__init__()
        self.animations = {"idle": [], "run": [], "jump": [], "fall": []}
        self.import_player_images()
        self.frame_index = 0
        self.image = self.animations["idle"][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # звуки
        self.jump_sound = pygame.mixer.Sound("data/effects/jump.wav")
        self.hit_sound = pygame.mixer.Sound("data/effects/hit.wav")
        self.heal_sound = pygame.mixer.Sound("data/effects/heal.wav")

        # движение
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -19
        self.face_to_right = True

        # статус модельки игрока
        self.status = "idle"
        self.on_ground = False
        self.on_left = False
        self.on_right = False
        self.on_top = False

        # хп
        self.change_health = change_health
        self.unreachable = False
        self.duration = 500
        self.hurt_time = 0

    def import_player_images(self):
        path = "graphics/character/"

        for animation in self.animations.keys():
            full_path = path + animation
            self.animations[animation] = import_folder(full_path)

    def get_status(self):
        if self.direction.y < 0:
            self.status = "jump"
        elif self.direction.y > 1:
            self.status = "fall"
        else:
            if self.direction.x != 0:
                self.status = "run"
            else:
                self.status = "idle"

    def get_input(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.left > 0:
            self.direction.x = -1
            self.face_to_right = False
        elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.right < 1280:
            self.direction.x = 1
            self.face_to_right = True
        else:
            self.direction.x = 0

        if keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.jump()

    def get_damage(self, amount):
        if not self.unreachable:
            self.change_health(amount)
            self.hit_sound.play()
            self.unreachable = True
            self.hurt_time = pygame.time.get_ticks()

    def get_health(self, amount):
        # игрок получает оверхил, потому что иначе пройти последнюю волну очень трудно
        self.change_health(amount)
        self.heal_sound.play()

    # метод недосягаемости
    def unreachability(self):
        # чтобы игрок не получал урон постоянно при соприкосновении с врагами вводим таймер и переменную
        if self.unreachable:
            time = pygame.time.get_ticks()
            if time - self.hurt_time >= self.duration:
                self.unreachable = False

    # значение для установки альфа параметра(прозрачности) получаем с помощью синусоиды
    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0

    def animate(self):
        animation = self.animations[self.status]

        # игрок прозрачен и создается эффект миганий
        if self.unreachable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

        self.frame_index += 0.15
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # отражение картинки игрока влево и вправо
        if self.face_to_right:
            self.image = animation[int(self.frame_index)]
        elif not self.face_to_right:
            self.image = pygame.transform.flip(animation[int(self.frame_index)], True, False)

        # для того, чтобы игрок не летал над поверхностью во время анимации простоя на месте
        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif self.on_top and self.on_right:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.on_top and self.on_left:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.on_top:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        if self.on_ground:
            self.direction.y = self.jump_speed
            self.jump_sound.play()
            self.jump_sound.set_volume(0.1)

    # постоянно обновляем нужные параметры
    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
        self.unreachability()
        self.wave_value()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.frame_index = 0
        self.animations = import_folder("graphics/enemy/run")
        self.death = import_folder("graphics/enemy/explosion")
        self.image = self.animations[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.health = 40
        self.enemy_type = "common"

        # движение
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = random.randint(4, 8)
        self.gravity = 0.8
        self.jump_speed = -20
        self.face_to_left = True
        self.on_ground = False
        self.can_jump = True

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.animations):
            self.frame_index = 0

        if self.face_to_left:
            self.image = self.animations[int(self.frame_index)]
        elif not self.face_to_left:
            self.image = pygame.transform.flip(self.animations[int(self.frame_index)], True, False)

    # метод преследования игрока
    def chase_player(self, hero):
        player = hero.sprite
        x_chase = player.rect.x
        if x_chase < self.rect.x:
            self.face_to_left = True
            self.direction.x = -1
        elif x_chase > self.rect.x:
            self.face_to_left = False
            self.direction.x = 1
        else:
            self.direction.x = 0

    # гравитация
    def apply_gravity(self):
        # враги появляются за картой, поэтому гравитацию применяем только когда они уже в поле зрения
        if 0 < self.rect.left < 1280:
            self.direction.y += self.gravity
            self.rect.y += self.direction.y

    def jump(self):
        if self.on_ground:
            self.direction.y = self.jump_speed

    def update(self):
        self.animate()


class Boss(Enemy):
    def __init__(self, pos, boss_type):
        super().__init__(pos)
        # параметры
        self.animations = {"idle": [], "move": [], "attack": []}
        self.boss_type = boss_type
        self.import_boss_images()
        self.image = self.animations["move"][self.frame_index]
        self.rect = self.image.get_rect(bottomleft=pos)
        self.enemy_type = "Boss"
        self.status = "move"
        # уникальные настройки для каждого босса
        if self.boss_type == "squid":
            self.health = 400
            self.speed = 4
            self.gravity_immune = False
            self.can_jump = True
        elif self.boss_type == "bamboo":
            self.health = 350
            self.can_jump = False
            self.gravity_immune = False
            self.speed = 3
        elif self.boss_type == "spirit":
            self.health = 250
            self.gravity_immune = True
            self.can_jump = False
            self.speed = 5

    def import_boss_images(self):
        path = f"graphics/{self.boss_type}/"

        for animation in self.animations.keys():
            full_path = path + animation
            self.animations[animation] = import_folder(full_path)

    def get_status(self):
        if self.direction.x != 0:
            self.status = "move"
        else:
            self.status = "idle"

    def chase_player(self, hero):
        # переопределяем метод, чтобы босс огонёк перемещался независимо от гравитации, и бамбук не падал в пропасть
        player = hero.sprite
        x_chase = player.rect.x
        y_chase = player.rect.y

        if self.boss_type == "spirit":
            if x_chase < self.rect.x:
                self.face_to_left = True
                self.direction.x = -1
            elif x_chase > self.rect.x:
                self.face_to_left = False
                self.direction.x = 1
            else:
                self.direction.x = 0
            if y_chase < self.rect.y:
                self.direction.y = -1
            elif y_chase > self.rect.y:
                self.direction.y = 1
        elif self.boss_type == "bamboo":
            if x_chase < self.rect.x and x_chase < 800:
                self.face_to_left = True
                self.direction.x = -1
            elif x_chase > self.rect.x and x_chase > 800:
                self.face_to_left = False
                self.direction.x = 0
            elif x_chase > self.rect.x:
                self.face_to_left = False
                self.direction.x = 1
            else:
                self.direction.x = 0
        else:
            # для осьминога оставляем обычные параметры преследования
            if x_chase < self.rect.x:
                self.face_to_left = True
                self.direction.x = -1
            elif x_chase > self.rect.x:
                self.face_to_left = False
                self.direction.x = 1
            else:
                self.direction.x = 0

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += 0.15
        if self.frame_index >= len(animation):
            self.frame_index = 0

        if self.face_to_left:
            self.image = animation[int(self.frame_index)]
        elif not self.face_to_left:
            self.image = pygame.transform.flip(animation[int(self.frame_index)], True, False)

    def apply_gravity(self):
        # огонёк игнорирует гравитацию
        if not self.gravity_immune:
            if 10 < self.rect.x < 1270:
                self.direction.y += self.gravity
                self.rect.y += self.direction.y

    def jump(self):
        if self.can_jump and self.on_ground:
            self.direction.y = self.jump_speed

    def update(self):
        self.get_status()
        self.animate()


# эффект взрыва врага
class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, animation_type):
        super().__init__()
        self.frame_index = 0
        if animation_type == "enemy death":
            self.frames = import_folder("graphics/enemy/explosion")
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self):
        # когда анимация прошла, убираем спрайт с карты
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()
