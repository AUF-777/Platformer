import pygame
import sys
import os

pygame.init()
pygame.mixer.init()
WIDTH = 800
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Platformer')
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 64)

GRAVITY = 0.8

# ==========================================================

# Формат строки:
# nickname;level;score
# ==========================================================
RECORDS_FILE = "records.txt"

# ==========================================================
BASE_LEVEL_WIDTH = 2200
LEVL_WIDTH = BASE_LEVEL_WIDTH

# ==========================================================
# КАРТИНКИ
# ==========================================================
bg_img = pygame.image.load('assets/image/bg.png')
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

player_img = pygame.image.load('assets/image/player (2).png')
player_img = pygame.transform.scale(player_img, (40, 50))

player_img_zerckal = pygame.image.load('assets/image/zerckal.png')
player_img_zerckal = pygame.transform.scale(player_img_zerckal, (40, 50))

enemy_img = pygame.image.load('assets/image/enemy.png')
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

portal_img = pygame.image.load('assets/image/portal.png')
portal_img = pygame.transform.scale(portal_img, (40, 60))

okonchan_img = pygame.image.load('assets/image/fon_okonchan.jpg')
okonchan_img = pygame.transform.scale(okonchan_img, (WIDTH, HEIGHT))

menu_img = pygame.image.load('assets/image/Menu.png')
menu_img = pygame.transform.scale(menu_img, (WIDTH, HEIGHT))

coin = [
    pygame.transform.scale(pygame.image.load('assets/image/coin1.png'), (20, 20)),
    pygame.transform.scale(pygame.image.load('assets/image/coin2.png'), (20, 20)),
    pygame.transform.scale(pygame.image.load('assets/image/coin3.png'), (20, 20)),
    pygame.transform.scale(pygame.image.load('assets/image/coin4.png'), (20, 20))
]
# ==========================================================
# Звуки
# ==========================================================

jump_sound = pygame.mixer.Sound('assets/sounds/jump.mp3')
Ydar_sound = pygame.mixer.Sound('assets/sounds/Ydar.mp3')
stol_sound = pygame.mixer.Sound('assets/sounds/stolknovenue_portal.mp3')
beg_sound = pygame.mixer.Sound('assets/sounds/beg.mp3')
knop_sound = pygame.mixer.Sound('assets/sounds/knop_menu.mp3')
over_sound = pygame.mixer.Sound('assets/sounds/game_over.mp3')
delete_sound = pygame.mixer.Sound('assets/sounds/Delete.mp3')
pad_menu_sound = pygame.mixer.Sound('assets/sounds/Pad_menu.mp3')
fon_menu_sound = pygame.mixer.Sound('assets/sounds/fon_menu.mp3')
collect_coins_sound = pygame.mixer.Sound('assets/sounds/collect_coins.mp3')
level_ganme_sound = pygame.mixer.Sound('assets/sounds/game_level.mp3')

# ==========================================================
# РАБОТА С РЕКОРДАМИ
# ==========================================================
def load_records():
    records = []

    if not os.path.exists(RECORDS_FILE):
        return records

    with open(RECORDS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            parts = line.split(";")

            if len(parts) != 4:
                continue

            nickname, level_text, score_text, difficulty = parts

            try:
                level = int(level_text)
                score = int(score_text)
                records.append((nickname, level, score, difficulty))
            except:
                pass

    # Сначала сортируем по уровню, потом по счёту
    records.sort(key=lambda item: (item[1], item[2]), reverse=True)
    return records[:5]


def save_record(nickname, level, score, difficulty):
    records = load_records()

    records.append((nickname, level, score, difficulty))
    records.sort(key=lambda item: (item[1], item[2]), reverse=True)
    records = records[:5]

    with open(RECORDS_FILE, "w", encoding="utf-8") as file:
        for nick, lvl, scr, difficulty in records:
            file.write(f"{nick};{lvl};{scr};{difficulty}\n")


class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

        self.platform_img = pygame.image.load('assets/image/platform.png')
        self.platform_img = pygame.transform.scale(self.platform_img, (self.rect.width, self.rect.height))

        self.platform_img2 = pygame.image.load('assets/image/platform_lefitat.png')
        self.platform_img2 = pygame.transform.scale(self.platform_img2, (self.rect.width, self.rect.height))

    def draw(self, surf, camera_x=0):
        surf.blit(self.platform_img, (self.rect.x - camera_x, self.rect.y))

    def draw2(self, surf, camera_x=0):
        surf.blit(self.platform_img2, (self.rect.x - camera_x, self.rect.y))


class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.frame = 0
        self.time = 0

    def update(self):
        self.time += 1

        if self.time >= 10:
            self.time = 0
            self.frame += 1

            if self.frame >= len(coin):
                self.frame = 0

    def draw(self, surf, camera_x=0):
        surf.blit(coin[self.frame], (self.rect.x - camera_x, self.rect.y))


class Enemy:
    def __init__(self, x, y, left_limit, right_limit):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 2
        self.dir = 1
        self.left_limit = left_limit
        self.right_limit = right_limit

    def update(self):
        self.rect.x += self.speed * self.dir

        if self.rect.left <= self.left_limit or self.rect.right >= self.right_limit:
            self.dir *= -1

    def draw(self, surf, camera_x=0):
        surf.blit(enemy_img, (self.rect.x - camera_x, self.rect.y))


class Player:
    def __init__(self, lives):
        self.rect = pygame.Rect(60, 300, 40, 50)

        self.vel_y = 0
        self.speed = 5
        self.on_ground = False

        self.lives = lives
        self.invuln = 0
        self.umage = player_img
        self.sound_beg = False

    def jump(self):
        if self.on_ground:
            jump_sound.play()
            self.vel_y = -14
            self.on_ground = False

    def hit(self):
        if self.invuln == 0:
            self.lives -= 1
            self.vel_y = -10
            self.invuln = 60
            if self.lives >= 1:
                Ydar_sound.play()

    def update(self, platforms):
        keys = pygame.key.get_pressed()

        dx = 0

        if keys[pygame.K_a]:
            self.umage = player_img_zerckal
            dx -= self.speed

        if keys[pygame.K_d]:
            self.umage = player_img
            dx += self.speed

        self.rect.x += dx

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > LEVL_WIDTH:
            self.rect.right = LEVL_WIDTH

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        self.on_ground = False

        for p in platforms:
            if self.rect.colliderect(p.rect) and self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.on_ground = True

        if self.rect.bottom > HEIGHT:
            self.lives = 0

        if self.invuln > 0:
            self.invuln -= 1

    def draw(self, surf, camera_x=0):
        if self.invuln > 0 and (self.invuln % 10) < 5:
            return

        surf.blit(self.umage, (self.rect.x - camera_x, self.rect.y))


class Game:
    def __init__(self):
        # start_menu — стартовое меню с топом игроков
        # nickname — ввод никнейма
        # difficulty — выбор сложности
        # play — игра
        # pause — пауза по ESC
        # game_over — проигрыш
        # finish — игрок дошёл до портала и может нажать E
        self.state = "start_menu"

        self.difficualty_name = 'Обычная' #Выбраная сложность

        self.nickname = ""
        self.start_lives = 3
        self.current_lives = 3
        self.level = 1

        # Чтобы результат записался в records.txt только один раз
        self.record_saved = False

        self.reset_level()

    def reset_level(self):
        global LEVL_WIDTH

        LEVL_WIDTH = BASE_LEVEL_WIDTH * self.level

        # ВАЖНО:
        # На первом уровне берём жизни из сложности.
        # На следующих уровнях берём текущие сохранённые жизни.
        self.player = Player(self.current_lives)

        self.Platforms2 = []
        for x in range(0, LEVL_WIDTH, 300):
            self.Platforms2.append(Platform(x, HEIGHT - 40, 400, 40))

        self.Platforms = []
        self.coins = []
        self.enemies = []

        for part in range(self.level):
            offset = part * BASE_LEVEL_WIDTH

            self.Platforms += [
                Platform(offset + 140, 330, 180, 40),
                Platform(offset + 380, 260, 180, 40),
                Platform(offset + 610, 320, 140, 40),
                Platform(offset + 900, 300, 250, 40),
                Platform(offset + 1200, 250, 200, 40),
                Platform(offset + 1500, 340, 220, 40),
                Platform(offset + 1800, 280, 220, 40)
            ]

            self.coins += [
                Coin(offset + 200, 300),
                Coin(offset + 430, 230),
                Coin(offset + 660, 290),
                Coin(offset + 980, 270),
                Coin(offset + 1260, 220),
                Coin(offset + 1560, 310),
                Coin(offset + 1900, 250)
            ]

            self.enemies += [
                Enemy(offset + 170, 290, offset + 140, offset + 320),
                Enemy(offset + 420, 220, offset + 380, offset + 540),
                Enemy(offset + 930, 260, offset + 900, offset + 1100),
                Enemy(offset + 1530, 300, offset + 1500, offset + 1680)
            ]

        self.score = 0
        self.camera_x = 0
        self.finish = pygame.Rect(LEVL_WIDTH - 150, HEIGHT - 100, 40, 60)

    def start_new_game(self, lives, difficulty_name):
        self.start_lives = lives
        self.current_lives = lives
        self.difficualty_name = difficulty_name
        self.level = 1
        self.record_saved = False
        self.state = "play"
        self.reset_level()

    def next_level(self):
        # Сохраняем жизни с предыдущего уровня и даём +1 жизнь
        self.current_lives = self.player.lives + 1
        level_ganme_sound.play()
        self.level += 1
        self.state = "play"
        self.reset_level()

    def save_result_once(self):
        if not self.record_saved:
            name = self.nickname.strip()

            if name == "":
                name = "Player"

            save_record(name, self.level, self.score, self.difficualty_name)
            self.record_saved = True

    def collect_coins(self):
        for c in self.coins[:]:
            if self.player.rect.colliderect(c.rect):
                collect_coins_sound.play()
                self.score += 1
                self.coins.remove(c)

    def enemy_hit(self):
        for e in self.enemies:
            if self.player.rect.colliderect(e.rect):
                self.player.hit()

    def check_finish(self):
        if self.player.rect.colliderect(self.finish):
            self.state = "finish"
            stol_sound.play()

    def update_camera(self):
        self.camera_x = max(
            0,
            min(self.player.rect.centerx - WIDTH // 2, LEVL_WIDTH - WIDTH)
        )

    def draw_records_on_start(self):
        # Топ игроков показывается только на стартовом экране
        records = load_records()

        title = font.render("ТОП 5 ИГРОКОВ:", True, (255, 255, 255))
        screen.blit(title, (30, 300))

        if len(records) == 0:
            empty = font.render("Пока рекордов нет", True, (255, 255, 255))
            screen.blit(empty, (30, 335))
            return

        y = 335
        for i, (nick, lvl, scr, diff) in enumerate(records, start=1):
            text = font.render(f"{i}. {nick} | уровень {lvl} | счёт {scr} | {diff}", True, (255, 255, 255))
            screen.blit(text, (30, y))
            y += 30

    def draw_world(self):
        screen.blit(bg_img, (0, 0))
        screen.blit(portal_img, (self.finish.x - self.camera_x, self.finish.y))

        for a in self.Platforms:
            a.draw2(screen, self.camera_x)

        for p in self.Platforms2:
            p.draw(screen, self.camera_x)

        for c in self.coins:
            c.draw(screen, self.camera_x)

        for e in self.enemies:
            e.draw(screen, self.camera_x)

        self.player.draw(screen, self.camera_x)

        screen.blit(font.render(f"Игрок: {self.nickname}", True, (0, 0, 0)), (10, 10))
        screen.blit(font.render(f"Уровень: {self.level}", True, (0, 0, 0)), (10, 40))
        screen.blit(font.render(f"Счёт: {self.score}", True, (0, 0, 0)), (10, 70))
        screen.blit(font.render(f"Жизни: {self.player.lives}", True, (0, 0, 0)), (10, 100))

    def draw_start_menu(self):
        screen.blit(menu_img, (0, 0))

        t1 = big_font.render("Platformer", True, (255, 255, 255))
        t2 = font.render("ENTER - начать игру", True, (255, 255, 255))
        t3 = font.render("Топ игроков показывается только здесь", True, (255, 255, 255))

        screen.blit(t1, t1.get_rect(center=(WIDTH / 2, 80)))
        screen.blit(t2, t2.get_rect(center=(WIDTH / 2, 150)))
        screen.blit(t3, t3.get_rect(center=(WIDTH / 2, 190)))

        self.draw_records_on_start()

    def draw_nickname_menu(self):
        screen.blit(menu_img, (0, 0))

        t1 = big_font.render("Введи никнейм", True, (255, 255, 255))
        t2 = font.render("Пиши с клавиатуры и нажми ENTER", True, (255, 255, 255))
        t3 = font.render(f"Ник: {self.nickname}", True, (255, 255, 0))

        screen.blit(t1, t1.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 90)))
        screen.blit(t2, t2.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 35)))
        screen.blit(t3, t3.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 25)))

    def draw_difficulty_menu(self):
        screen.blit(menu_img, (0, 0))

        t1 = big_font.render("Выбери сложность", True, (255, 255, 255))
        t2 = font.render("1 - Лёгкая: 5 жизней", True, (255, 255, 255))
        t3 = font.render("2 - Обычная: 3 жизни", True, (255, 255, 255))
        t4 = font.render("3 - Сложная: 1 жизнь", True, (255, 255, 255))

        screen.blit(t1, t1.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 90)))
        screen.blit(t2, t2.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20)))
        screen.blit(t3, t3.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))
        screen.blit(t4, t4.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 60)))

    def draw_pause_menu(self):
        screen.blit(menu_img, (0, 0))

        t1 = big_font.render("Пауза", True, (255, 255, 255))
        t2 = font.render("ESC - продолжить игру", True, (255, 255, 255))
        t3 = font.render("R - стартовое меню", True, (255, 255, 255))
        t4 = font.render("Q - выйти из игры", True, (255, 255, 255))

        screen.blit(t1, t1.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 70)))
        screen.blit(t2, t2.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 10)))
        screen.blit(t3, t3.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 30)))
        screen.blit(t4, t4.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 70)))

    def draw_game_over(self):
        screen.blit(okonchan_img, (0, 0))

        t1 = big_font.render("Ты проиграл", True, (255, 255, 255))
        t2 = font.render("Результат сохранён", True, (255, 255, 255))
        t3 = font.render("R или ESC - стартовое меню", True, (255, 255, 255))

        screen.blit(t1, t1.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50)))
        screen.blit(t2, t2.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 10)))
        screen.blit(t3, t3.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 45)))

    def draw_finish_screen(self):
        self.draw_world()

        t1 = big_font.render("Портал найден!", True, (0, 0, 0))
        t2 = font.render("E - следующий уровень", True, (0, 0, 0))
        t3 = font.render(f"Жизни сохранятся и будет {self.player.lives} + 1", True, (0, 0, 0))

        screen.blit(t1, t1.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 60)))
        screen.blit(t2, t2.get_rect(center=(WIDTH / 2, HEIGHT / 2)))
        screen.blit(t3, t3.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 40)))

    def update_game(self):
        if self.state == "play":
            self.player.update(self.Platforms + self.Platforms2)

            for c in self.coins:
                c.update()

            for e in self.enemies:
                e.update()

            self.enemy_hit()
            self.collect_coins()

            if self.player.lives <= 0:
                over_sound.play()
                self.save_result_once()
                self.state = "game_over"

            self.check_finish()
            self.update_camera()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:

                    # СТАРТОВОЕ МЕНЮ
                    if self.state == "start_menu":
                        if event.key == pygame.K_RETURN:
                            pad_menu_sound.play()
                            self.nickname = ""
                            self.state = "nickname"

                    # ВВОД НИКНЕЙМА
                    elif self.state == "nickname":
                        if event.key == pygame.K_RETURN:
                            pad_menu_sound.play()
                            if self.nickname.strip() == "":
                                self.nickname = "Player"

                            self.state = "difficulty"

                        elif event.key == pygame.K_BACKSPACE:
                            delete_sound.play()
                            self.nickname = self.nickname[:-1]

                        else:
                            # Добавляем символ в ник, если он не слишком длинный
                            if len(self.nickname) < 12 and event.unicode.strip() != "":
                                knop_sound.play()
                                self.nickname += event.unicode

                    # ВЫБОР СЛОЖНОСТИ
                    elif self.state == "difficulty":
                        if event.key == pygame.K_1:
                            pad_menu_sound.play()
                            self.start_new_game(5, "Лёгкая")

                        if event.key == pygame.K_2:
                            pad_menu_sound.play()
                            self.start_new_game(3, "Обычная")

                        if event.key == pygame.K_3:
                            pad_menu_sound.play()
                            self.start_new_game(1, "Сложная")

                    # ИГРА
                    elif self.state == "play":
                        if event.key == pygame.K_SPACE:
                            self.player.jump()

                        if event.key == pygame.K_ESCAPE:
                            pad_menu_sound.play()
                            self.state = "pause"

                    # ПАУЗА
                    elif self.state == "pause":
                        if event.key == pygame.K_ESCAPE:
                            pad_menu_sound.play()
                            self.state = "play"

                        if event.key == pygame.K_r:
                            self.save_result_once()
                            pad_menu_sound.play()
                            self.state = "start_menu"

                        if event.key == pygame.K_q:
                            self.save_result_once()
                            running = False

                    # ПОРТАЛ
                    elif self.state == "finish":
                        if event.key == pygame.K_e:
                            self.next_level()

                        if event.key == pygame.K_ESCAPE:
                            pad_menu_sound.play()
                            self.state = "pause"

                    # ПРОИГРЫШ
                    elif self.state == "game_over":
                        if event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                            pad_menu_sound.play()
                            self.state = "start_menu"

            self.update_game()

            if self.state == "start_menu":
                self.draw_start_menu()

            elif self.state == "nickname":
                self.draw_nickname_menu()

            elif self.state == "difficulty":
                self.draw_difficulty_menu()

            elif self.state == "play":
                self.draw_world()

            elif self.state == "pause":
                self.draw_pause_menu()

            elif self.state == "finish":
                self.draw_finish_screen()

            elif self.state == "game_over":
                self.draw_game_over()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


Game().run()
