import pygame, random, sys
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((400, 600))
pygame.display.set_caption("lab11_racer_final")
clk = pygame.time.Clock()

f1 = pygame.font.SysFont("Verdana", 20)
f2 = pygame.font.SysFont("Verdana", 60)

spd = 5
sc = 0
monetki = 0
next_lvl = 5 # предел монет для ускорения

class Vrag(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, 360), 0)

    def move(self):
        global sc
        self.rect.move_ip(0, spd) 
        if self.rect.top > 600:
            sc += 1 
            self.rect.top = 0
            self.rect.center = (random.randint(40, 360), 0)

class Ya(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 60))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520) 

    def move(self):
        k = pygame.key.get_pressed()
        if k[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)
        if k[K_RIGHT] and self.rect.right < 400:
            self.rect.move_ip(5, 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((25, 25))
        self.rect = self.image.get_rect()
        self.respawn()

    def respawn(self):
        # 1 - обычная, 3 - крутая (вероятность 25%)
        self.weight = random.choice([1, 1, 1, 3]) 
        if self.weight == 1:
            self.image.fill((255, 215, 0)) # желтая
        else:
            self.image.fill((255, 0, 255)) # фиолетовая
            
        self.rect.top = -50
        self.rect.center = (random.randint(40, 360), -50)

    def move(self):
        self.rect.move_ip(0, spd)
        if self.rect.top > 600:
            self.respawn()

p1 = Ya()
v1 = Vrag()
c1 = Coin()

vragi_grp, coins_grp, all_spr = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
vragi_grp.add(v1)
coins_grp.add(c1)
all_spr.add(p1, v1, c1)

while 1:
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit() 
            
    screen.fill((255, 255, 255))
    
    txt1 = f1.render(f"Score: {sc}", True, (0, 0, 0))
    txt2 = f1.render(f"Coins: {monetki}", True, (0, 0, 0))
    screen.blit(txt1, (10, 10))
    screen.blit(txt2, (400 - txt2.get_width() - 10, 10)) 

    for s in all_spr:
        s.move()
        screen.blit(s.image, s.rect)
        
    # монетки с весом
    if pygame.sprite.spritecollideany(p1, coins_grp):
        monetki += c1.weight
        c1.respawn()
        
        # логика ускорения
        if monetki >= next_lvl:
            spd += 1
            next_lvl += 5 # каждые 5 монет будет сложнее

    if pygame.sprite.spritecollideany(p1, vragi_grp):
        screen.fill((255, 0, 0))
        gg = f2.render("CRASHED!", True, (0, 0, 0))
        screen.blit(gg, (400 // 2 - gg.get_width() // 2, 600 // 2 - gg.get_height() // 2))
        pygame.display.update()
        pygame.time.wait(2000)
        sys.exit() 

    pygame.display.update()
    clk.tick(60)