import pygame
import sys
import os
from level import Level
from game_data import level_0
from user_interface import UserInterface


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


def load_sound(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Звуковой файл '{fullname}' не найден")
        sys.exit()
    pygame.mixer.music.load(fullname)


pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Survive them ALL")
pygame.display.set_icon(pygame.image.load("graphics/spirit/attack/0.png"))
load_sound("main_theme.mp3")
clock = pygame.time.Clock()
FPS = 60


class Button:
    def __init__(self, image_name, x, y, font_name, font_size, text, base_color, hovering_color):
        self.image = load_image(image_name)
        self.x = x
        self.y = y
        self.font = load_font(font_name, font_size)
        self.text = text
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text
        self.text = self.font.render(self.text_input, True, self.base_color)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    # функция отрисовки кнопки на экране
    def update(self, screen):
        # устанавливаем фон кнопки
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    # проверяем, находится ли мышь на кнопке
    def check_mouse_contact(self, pos):
        if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
            return True
        else:
            return False

    # если навести мышь на кнопку, то цвет текста изменяется
    def change_color(self, pos):
        if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


# класс игры (создан для реализации интерфейса)
class Game:
    def __init__(self):
        self.max_health = 100
        self.current_health = 100
        self.coins = 0

        self.level = Level(level_0, screen, self.change_score, self.change_health)
        self.ui = UserInterface(screen)

    def change_score(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.current_health += amount

    def run(self):
        self.level.run()
        self.ui.show_wave_number(self.level.wave_number)
        self.ui.show_health_bar(self.current_health, self.max_health)
        self.ui.show_coins(self.coins)
        self.ui.show_damage_frame(self.current_health)


# функция, запускающая саму игру
def start_game():
    pygame.mixer.music.stop()
    game = Game()
    # фоновая музыка
    level_bg_music = pygame.mixer.Sound("data/level_music.wav")
    level_bg_music.play(loops=-1)
    level_bg_music.set_volume(0.05)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    level_bg_music.stop()
                    main_menu()
                    running = False
        if game.current_health <= 0:
            level_bg_music.stop()
            end_game(game.coins)
            running = False
        if game.level.win_game:
            level_bg_music.stop()
            win_game(game.coins)
            with open("win_trophy.txt", "w") as file:
                file.write("win")
                file.close()
            running = False

        screen.fill("black")
        game.run()
        pygame.display.flip()
        clock.tick(FPS)


# экран конца игры при победе
def win_game(score):
    pygame.mixer.stop()
    running = True
    exit_button = Button("Quit Rect.png", 620, 550, "font.ttf", 75, "EXIT", "#d7fcd4", "white")
    background = load_image("Background.png")

    while running:
        screen.blit(background, (0, 0))

        win_text = load_font("font.ttf", 100).render("YOU WIN", True, "#b68f40")
        win_rect = win_text.get_rect(center=(640, 100))
        score_text = load_font("font.ttf", 75).render(f"SCORE: {score}", True, "white")
        score_rect = score_text.get_rect(midleft=(300, 320))

        screen.blit(win_text, win_rect)
        screen.blit(score_text, score_rect)
        exit_button.change_color(pygame.mouse.get_pos())
        exit_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_mouse_contact(pygame.mouse.get_pos()):
                    main_menu()
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    running = False
        pygame.display.flip()


# экран конца игры по причине смерти игрока
def end_game(score):
    pygame.mixer.stop()
    running = True
    exit_button = Button("Quit Rect.png", 620, 550, "font.ttf", 75, "EXIT", "#d7fcd4", "white")

    while running:
        screen.fill("black")

        end_text = load_font("font.ttf", 100).render("YOU DIED", True, "#dc4949")
        end_rect = end_text.get_rect(center=(640, 120))
        score_text = load_font("font.ttf", 75).render(f"SCORE: {score}", True, "white")
        score_rect = score_text.get_rect(midleft=(250, 320))

        screen.blit(score_text, score_rect)
        screen.blit(end_text, end_rect)
        exit_button.change_color(pygame.mouse.get_pos())
        exit_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_mouse_contact(pygame.mouse.get_pos()):
                    main_menu()
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    running = False
        pygame.display.flip()


# функция, отвечающая за вкладку настроек
def settings():
    background = load_image("Background.png")
    pygame.display.set_caption("Options")

    back_button = Button("Play Rect.png", 640, 550, "font.ttf", 75, "BACK", "#d7fcd4", "white")

    running = True
    while running:
        screen.blit(background, (0, 0))

        back_button.change_color(pygame.mouse.get_pos())
        back_button.update(screen)
        settings_text = load_font("font.ttf", 75).render("Coming soon", True, "white")
        settings_rect = settings_text.get_rect(center=(640, 320))

        screen.blit(settings_text, settings_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_mouse_contact(pygame.mouse.get_pos()):
                    main_menu()
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    running = False

        pygame.display.flip()


# появляется перед началом игры
def controls_panel():
    running = True

    play_button = Button("Play Rect.png", 640, 650, "font.ttf", 75, "FINE", "#d7fcd4", "white")

    space_key = load_image("Space-Key.png")
    space_key_rect = space_key.get_rect(center=(256, 256))
    w_key = load_image("W-Key.png")
    w_key_rect = w_key.get_rect(center=(128, 256))
    jump_text = load_font("font.ttf", 64).render("jump", True, "white")
    jump_text_rect = jump_text.get_rect(midleft=(340, 256))

    a_key = load_image("A-Key.png")
    a_key_rect = a_key.get_rect(center=(128, 384))
    a_text = load_font("font.ttf", 64).render("run left", True, "white")
    a_text_rect = a_text.get_rect(midleft=(192, 384))

    d_key = load_image("D-Key.png")
    d_key_rect = d_key.get_rect(center=(128, 512))
    d_text = load_font("font.ttf", 64).render("run right", True, "white")
    d_text_rect = d_text.get_rect(midleft=(192, 512))

    esc_key = load_image("Esc-Key.png")
    esc_key_rect = esc_key.get_rect(center=(720, 256))
    esc_text = load_font("font.ttf", 64).render("menu", True, "white")
    esc_text_rect = esc_text.get_rect(midleft=(784, 256))

    while running:
        screen.fill("black")
        controls_text = load_font("font.ttf", 75).render("Controls", True, "white")
        controls_rect = controls_text.get_rect(center=(640, 100))

        screen.blit(w_key, w_key_rect)
        screen.blit(a_key, a_key_rect)
        screen.blit(d_key, d_key_rect)
        screen.blit(space_key, space_key_rect)
        screen.blit(esc_key, esc_key_rect)

        screen.blit(jump_text, jump_text_rect)
        screen.blit(a_text, a_text_rect)
        screen.blit(d_text, d_text_rect)
        screen.blit(esc_text, esc_text_rect)

        screen.blit(controls_text, controls_rect)
        play_button.change_color(pygame.mouse.get_pos())
        play_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_mouse_contact(pygame.mouse.get_pos()):
                    start_game()
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    running = False

        pygame.display.flip()


# функция, отвечающая за главное меню
def main_menu():
    # если музыка уже не играет, то запускаем её
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)
    background = load_image("Background.png")
    play_button = Button("Play Rect.png", 640, 250, "font.ttf", 75, "PLAY", "#d7fcd4", "white")
    settings_button = Button("Options Rect.png", 640, 400, "font.ttf", 75, "OPTIONS", "#d7fcd4", "white")
    quit_button = Button("Quit Rect.png", 640, 550, "font.ttf", 75, "QUIT", "#d7fcd4", "white")

    coin = pygame.image.load("graphics/ui/coin.png")
    circle_radius = 32
    size = 1280, 720
    circle = [[32, 32], [1248, 688]]
    speed = [[-2, -2], [2, 2]]

    win_trophy_surface = pygame.Surface((96, 56), flags=pygame.SRCALPHA)
    win_trophy_rect = win_trophy_surface.get_rect(bottomleft=(64, 656))
    # при последующих запусках игры в главном меню появится трофей за победу
    with open("win_trophy.txt") as file:
        win = file.read()
        if win == "win":
            win_trophy_surface = pygame.image.load("graphics/character/hat.png")
        file.close()

    running = True
    while running:
        screen.blit(background, (0, 0))

        for i in range(len(circle)):
            if circle[i][0] <= circle_radius:
                speed[i][0] = speed[i][0] * -1
            if circle[i][0] >= size[0] - circle_radius:
                speed[i][0] = speed[i][0] * -1
            if circle[i][1] <= circle_radius:
                speed[i][1] = speed[i][1] * -1
            if circle[i][1] >= size[1] - circle_radius:
                speed[i][1] = speed[i][1] * -1
            circle[i][0] += speed[i][0]
            circle[i][1] += speed[i][1]
            screen.blit(coin, circle[i])

        menu_text = load_font("font.ttf", 100).render("MAIN MENU", True, "#b68f40")
        menu_rect = menu_text.get_rect(center=(640, 100))
        screen.blit(win_trophy_surface, win_trophy_rect)

        screen.blit(menu_text, menu_rect)

        # отрисовываем все кнопки и устанавливаем цвет текста
        for button in [play_button, settings_button, quit_button]:
            button.change_color(pygame.mouse.get_pos())
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_mouse_contact(pygame.mouse.get_pos()):
                    controls_panel()
                    running = False
                if settings_button.check_mouse_contact(pygame.mouse.get_pos()):
                    settings()
                    running = False
                if quit_button.check_mouse_contact(pygame.mouse.get_pos()):
                    sys.exit()

        pygame.display.flip()


main_menu()
pygame.quit()
