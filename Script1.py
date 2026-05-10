import pygame
import sys
pygame.init()

WIDTH = 800
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Platformer')
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 64)

GRAVITY = 0.8

#-------подготовка к камере--------
LEVL_WIDTH = 2200

bg_img = pygame.image.load('assets/image/bg.png')
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

player_img = pygame.image.load('assets/image/player (2).png')
player_img = pygame.transform.scale(player_img, (40,50))
player_img_zerckal = pygame.image.load('assets/image/zerckal.png')
player_img_zerckal = pygame.transform.scale(player_img_zerckal, (40,50))

enemy_img = pygame.image.load('assets/image/enemy.png')
enemy_img = pygame.transform.scale(enemy_img, (40,40))


portal_img = pygame.image.load('assets/image/portal.png')
portal_img = pygame.transform.scale(portal_img, (40,60))

okonchan_img = pygame.image.load('assets/image/fon_okonchan.jpg')
okonchan_img = pygame.transform.scale(okonchan_img, (WIDTH,HEIGHT))

menu_img = pygame.image.load('assets/image/Menu.png')
menu_img = pygame.transform.scale(menu_img, (WIDTH,HEIGHT))

coin = [
    pygame.transform.scale(pygame.image.load('assets/image/coin1.png'), (20,20)),
    pygame.transform.scale(pygame.image.load('assets/image/coin2.png'), (20,20)),
    pygame.transform.scale(pygame.image.load('assets/image/coin3.png'), (20,20)),
    pygame.transform.scale(pygame.image.load('assets/image/coin4.png'), (20,20))
]

class Platform:
    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x, y, w, h)
        self.platform_img = pygame.image.load('assets/image/platform.png')
        self.platform_img = pygame.transform.scale(self.platform_img, (self.rect.width, self.rect.height))
        self.platform_img2 = pygame.image.load('assets/image/platform_lefitat.png')
        self.platform_img2 = pygame.transform.scale(self.platform_img2, (self.rect.width, self.rect.height))
    def draw(self, surf, camera_x = 0):
        screen.blit(self.platform_img, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h))
    def draw2(self, surf, camera_x = 0):
        screen.blit(self.platform_img2, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h))
class Coin:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.frame = 0
        self.time = 0

    def update(self):
        self.time += 1
        if self.time >= 10:
            self.time = 0
            self.frame += 1
            if self.frame >=len(coin):
                self.frame = 0

    def draw(self, surf, camera_x = 0):
        screen.blit(coin[self.frame], (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h))
class Enemy:
    def __init__(self,x,y, left_limit, right_limit):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 2
        self.dir = 1
        self.left_limit = left_limit
        self.right_limit = right_limit
    def update(self):
        self.rect.x += self.speed * self.dir

        if self.rect.left <= self.left_limit or self.rect.right >= self.right_limit:
            self.dir *= -1

    def draw(self, surf, camera_x = 0):
        screen.blit(enemy_img, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(60,300,40,50)

        self.vel_y = 0
        self.speed = 5
        self.on_ground = False

        self.lives = 3
        self.invuln = 0
        self.umage = player_img

    def jump(self):

        if self.on_ground:
            self.vel_y = -14
            self.on_ground = False
    def hit(self):

        if self.invuln == 0 :
            self.lives -= 1
            self.vel_y = -10
            self.invuln = 60

    def update(self, Platform):

        key = pygame.key.get_pressed()

        dx = 0
        if key[pygame.K_a]:
            self.umage = player_img_zerckal
            dx -= self.speed
        if key[pygame.K_d]:
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

        for p in Platform:
            if self.rect.colliderect(p.rect) and self.vel_y > 0:

                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.on_ground = True

        if self.rect.bottom > HEIGHT:
            self.lives = 0

        if self.invuln > 0:
            self.invuln -= 1

    def draw(self, surf, camera_x = 0):

        if self.invuln > 0 and (self.invuln % 10) < 5:
            return
        screen.blit(self.umage, (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h))

class Game:
    def __init__(self):
        self.reset()
    def reset(self):
        self.player = Player()

        self.Platforms2 = []

        for x in range(0, LEVL_WIDTH, 300):
            self.Platforms2.append(Platform(x, HEIGHT - 40, 400, 40))

        self.Platforms2 += []

        self.Platforms = [
            Platform(140, 330, 180, 40),
            Platform(380,260,180,40),
            Platform(610,320,140,40),
            Platform(900, 300, 250, 40),
            Platform(1200, 250, 200, 40),
            Platform(1500, 340, 220, 40),
            Platform(1800, 280, 220, 40)
        ]


        self.coins = [
            Coin(200,300),
            Coin(430, 230),
            Coin(660, 290),
            Coin(980, 270),
            Coin(1260, 220),
            Coin(1560, 310),
            Coin(1900, 250)
        ]

        self.enemies = [
            Enemy(170,290,140,320),
            Enemy(420, 220, 380, 540),
            Enemy(930, 260, 900, 1100),
            Enemy(1530, 300, 1500, 1680)
        ]

        self.score = 0
        self.game_over = False
        self.menu = False
        self.camera_x = 0
        self.finish = pygame.Rect(2050, HEIGHT - 100, 40, 60)

    def collect_coins(self):
        for c in self.coins[:]:
            if self.player.rect.colliderect(c.rect):
                self.score += 1
                self.coins.remove(c)
    def enemy_hit(self):
        for e in self.enemies[:]:
            if self.player.rect.colliderect(e.rect):
                self.player.hit()

    def check_finish(self):
        if self.player.rect.colliderect(self.finish):
            print("Ты выйграл")

    def update_camera(self):

        self.camera_x = max(0, min(self.player.rect.centerx - WIDTH // 2, LEVL_WIDTH - WIDTH))
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE and not self.game_over and not self.menu:
                        self.player.jump()
                    if event.key == pygame.K_r and self.game_over and not self.menu or self.menu:
                        self.reset()
                        self.game_over = False
                        self.menu = False
                    if event.key == pygame.K_ESCAPE and not self.menu:
                        self.menu = True
                        self.game_over = False
                    if event.key == pygame.K_q and self.menu:
                        running = False



            if not self.game_over and not self.menu:

                self.player.update(self.Platforms + self.Platforms2)

                for c in self.coins:
                    c.update()

                for e in self.enemies:
                    e.update()
                self.enemy_hit()
                self.collect_coins()

                if self.player.lives <= 0:
                    self.game_over = True
                self.check_finish()
                self.update_camera()

                screen.blit(bg_img, (0,0))
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

            screen.blit(font.render(f"Счёт: {self.score}", True, (0, 0, 0)), (10, 10))
            screen.blit(font.render(f"Жизни : {self.player.lives}", True, (0, 0, 0)), (10, 40))

            if self.menu:
                screen.blit(menu_img, (0, 0))
                t1 = big_font.render("Меню", True, (255, 255, 255))
                t2 = font.render("Нажми R начало игры", True, (255, 255, 255))
                t3 = font.render("Нажми Q для выхода из игры", True, (255, 255, 255))
                screen.blit(t3, t3.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 45)))
                screen.blit(t2, t2.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 25)))
                screen.blit(t1, t1.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20)))

            if self.game_over:
                screen.blit(okonchan_img, (0, 0))

                t1 = big_font.render("Ты проиграл", True, (255, 255, 255))
                t2 = font.render("Нажми R для повторной игры", True, (255, 255, 255))
                t3 = font.render("Нажми ESC для выхода в меню", True, (255, 255, 255))
                screen.blit(t1, t1.get_rect(center=(WIDTH/2, HEIGHT/2 - 20)))
                screen.blit(t2, t2.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 25)))
                screen.blit(t3, t3.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 45)))
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()
Game().run()
