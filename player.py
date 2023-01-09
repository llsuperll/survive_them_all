import pygame
from support import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.animations = {"idle": [], "run": [], "jump": [], "fall": []}
        self.import_player_images()
        self.frame_index = 0
        self.image = self.animations["idle"][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # звуки
        self.jump_sound = pygame.mixer.Sound("data/effects/jump.wav")
        self.hit_sound = pygame.mixer.Sound("data/effects/hit.wav")

        # движение
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -19
        self.face_to_right = True
        self.status = "idle"
        self.on_ground = False
        self.on_left = False
        self.on_right = False
        self.on_top = False

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
        if keys[pygame.K_a] and self.rect.left > 0:
            self.direction.x = -1
            self.face_to_right = False
        elif keys[pygame.K_d] and self.rect.right < 1280:
            self.direction.x = 1
            self.face_to_right = True
        else:
            self.direction.x = 0

        if keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.jump()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += 0.15
        if self.frame_index >= len(animation):
            self.frame_index = 0

        if self.face_to_right:
            self.image = animation[int(self.frame_index)]
        elif not self.face_to_right:
            self.image = pygame.transform.flip(animation[int(self.frame_index)], True, False)

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

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
