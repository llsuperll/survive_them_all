import pygame


class UserInterface:
    def __init__(self, surface):
        self.surface = surface
        self.health_bar = pygame.image.load("graphics/ui/health_bar.png")
        self.health_bar_width = 152
        self.health_bar_height = 4

        self.coin = pygame.image.load("graphics/ui/coin.png")
        self.coin_rect = self.coin.get_rect(topleft=(50, 61))
        self.font = pygame.font.Font("data/font.ttf", 30)
        self.damage_frame = pygame.image.load("data/damage.png")
        self.damage_frame.set_alpha(0)
        self.damage_effect = pygame.image.load("data/damage2.png")
        self.damage_effect.set_alpha(0)

    # сумма монет на экране
    def show_coins(self, amount):
        self.surface.blit(self.coin, self.coin_rect)
        coin_amount_surface = self.font.render(str(amount), False, "#33323d")
        coin_amount_rect = coin_amount_surface.get_rect(midleft=(self.coin_rect.right + 4, self.coin_rect.centery))
        self.surface.blit(coin_amount_surface, coin_amount_rect)

    # отображение полоски хп
    def show_health_bar(self, current, full):
        self.surface.blit(self.health_bar, (20, 10))
        if current > full:
            current = full
        # т.к. кол-во хп игрока и размер хп бара различны, то нужно найти такой коэффициент,
        # чтобы красная полоска не вылезала за пределы бара
        current_health_coef = current / full
        current_bar_width = self.health_bar_width * current_health_coef
        health_bar_rect = pygame.Rect((54, 39), (current_bar_width, self.health_bar_height))
        pygame.draw.rect(self.surface, "#dc4949", health_bar_rect)

    # номер волны
    def show_wave_number(self, wave_number):
        wave_number = wave_number
        wave_surface = self.font.render("WAVE:", False, "black")
        wave_rect = wave_surface.get_rect(topleft=(250, 30))
        wave_num_surface = self.font.render(str(wave_number), False, "black")
        wave_num_rect = wave_num_surface.get_rect(topleft=(400, 30))
        self.surface.blit(wave_surface, wave_rect)
        self.surface.blit(wave_num_surface, wave_num_rect)

    # рамка урона
    def show_damage_frame(self, current_hp):
        if current_hp > 80:
            self.damage_frame.set_alpha(0)
            self.damage_effect.set_alpha(0)
        elif 60 <= current_hp <= 80:
            self.damage_frame.set_alpha(20)
        elif 40 <= current_hp < 60:
            self.damage_frame.set_alpha(60)
            self.damage_effect.set_alpha(60)
        self.surface.blit(self.damage_frame, (0, 0))
        self.surface.blit(self.damage_effect, (-200, 120))
