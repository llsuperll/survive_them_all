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

    def show_coins(self, amount):
        self.surface.blit(self.coin, self.coin_rect)
        coin_amount_surface = self.font.render(str(amount), False, "#33323d")
        coin_amount_rect = coin_amount_surface.get_rect(midleft=(self.coin_rect.right + 4, self.coin_rect.centery))
        self.surface.blit(coin_amount_surface, coin_amount_rect)

    def show_health_bar(self, current, full):
        self.surface.blit(self.health_bar, (20, 10))
        current_health_coef = current / full
        current_bar_width = self.health_bar_width * current_health_coef
        health_bar_rect = pygame.Rect((54, 39), (current_bar_width, self.health_bar_height))
        pygame.draw.rect(self.surface, "#dc4949", health_bar_rect)
