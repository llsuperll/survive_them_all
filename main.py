import pygame
import sys
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_font(name, size):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с шрифтом '{fullname}' не найден")
        sys.exit()
    font = pygame.font.Font(fullname, size)
    return font


pygame.init()
screen = pygame.display.set_mode((1280, 720))


class Button:
    def __init__(self, image_name, x, y, font_name, text, base_color, hovering_color):
        self.image = load_image(image_name)
        self.x = x
        self.y = y
        self.font = load_font(font_name, 75)
        self.text = text
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_input(self, pos):
        if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
            return True
        else:
            return False

    def change_color(self, pos):
        if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


def start_game():
    pass


def settings():
    pass


def main_menu():
    background = load_image("Background.png")
    pygame.display.set_caption("Menu")
    play_button = Button("Play Rect.png", 640, 250, "font.ttf", "PLAY", "#d7fcd4", "white")
    settings_button = Button("Options Rect.png", 640, 400, "font.ttf", "OPTIONS", "#d7fcd4", "white")
    quit_button = Button("Quit Rect.png", 640, 550, "font.ttf", "QUIT", "#d7fcd4", "white")

    running = True
    while running:
        screen.blit(background, (0, 0))
        menu_text = load_font("font.ttf", 100).render("MAIN MENU", True, "#b68f40")
        menu_rect = menu_text.get_rect(center=(640, 100))

        screen.blit(menu_text, menu_rect)

        for button in [play_button, settings_button, quit_button]:
            button.change_color(pygame.mouse.get_pos())
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_input(pygame.mouse.get_pos()):
                    start_game()
                if settings_button.check_input(pygame.mouse.get_pos()):
                    settings()
                if quit_button.check_input(pygame.mouse.get_pos()):
                    running = False
        pygame.display.flip()


main_menu()
pygame.quit()
