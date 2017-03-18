import pygame
import os
import time
import random

from level import Level
from camera import Camera
from objects import Player, Changing, Platform
from images import SIZE, SPEED_SHIFT, images
global unlocked, entities, player1
player1 = None
entities = pygame.sprite.Group()
unlocked = []

WIN_WIDTH = 800#1280
WIN_HEIGHT = 640#800
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), 0, 32)

HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)


def destroy(e):
    e.show = False
    e.rect.width = e.rect.height = 0
    e.rect.top = e.rect.left = 1923781470398 #get outta here

def revive(e):
    e.show = True
    e.rect.width = e.rect.height = SIZE
    e.rect.top = e.x
    e.rect.left = e.y
    
def unlock(_type, platforms=entities, rep=' '):
    for i in platforms:
        if i.type == _type:
            destroy(i)

def full_blit(bg, camera):
    for x in range(WIN_WIDTH//SIZE):
        for y in range(WIN_HEIGHT//SIZE):
            screen.blit(bg, (x * SIZE, y * SIZE))
            
    global entities, player1
    moved = player1.moved
    if moved is not None:
        for e in entities:
            if isinstance(e, Changing):
                e.check(moved)                  
    for e in entities:
        if e.show:
            screen.blit(e.image, camera.apply(e))

def run(l):
    level = Level(SIZE, SIZE, l)
    level.start()
    
    p1 = next(level.find('@'))
    global player1
    player1 = Player(p1[0]*SIZE, p1[1]*SIZE, level, 5)
    
    bg = pygame.Surface((SIZE,SIZE))
    bg.convert()
    bg.fill(pygame.Color("#000000"))
    
    clock = pygame.time.Clock()
    
    global entities
    for p in level.platforms:
        entities.add(p)
    for e in level.enemies:
        entities.add(e)
    for e in level.movers:
        entities.add(e)
    entities.add(player1)
        
    total_level_width  = len(level.level[0])*SIZE
    total_level_height = len(level.level)*SIZE
    camera = Camera(total_level_width, total_level_height)

    up = left = right = False
    i=0
    while not player1.won:
        clock.tick(60)
        screen.fill((255, 255, 255))
        
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                   up = True
                if e.key == pygame.K_LEFT:
                    left = True
                if e.key == pygame.K_RIGHT:
                    right = True

            if e.type == pygame.KEYUP:
                if e.key == pygame.K_UP:
                    up = False
                if e.key == pygame.K_RIGHT:
                    right = False
                if e.key == pygame.K_LEFT:
                    left = False
                

                
        player1.run(up, left, right)
        for _t in player1.unlocked:
            unlock(_t)
        camera.update(player1)

        if i % 3/SPEED_SHIFT == 0:
            player1.frameset()
        if i % 6/SPEED_SHIFT == 0:
            for e in level.enemies:
                e.animate(player1)
        i += 1

        full_blit(bg, camera)
        pygame.display.update()
        
##    for (i,p) in enumerate(level.platforms):
##        if p.type == 'E':
##            t = (i,p)
##        if p.type == 'F':
##            b = i,p
##    a=Platform(t[1].x, t[1].y, images['G'])
##    c=Platform(b[1].x, b[1].y, images['H'])
##    level.platforms[t[0]] = a
##    level.platforms[b[0]] = c
    for (i,p) in enumerate(level.platforms):
        if p.type == 'I':
            t = (i,p)
    a=Platform(t[1].x, t[1].y, images['J'])
    level.platforms[t[0]] = a   
    entities.remove(t[1])
    entities.add(a)
    full_blit(bg, camera)
    pygame.display.update()

    player1.fall()
    player1.frameset()
    destroy(player1)
    #player1.rect.left -= SIZE
    full_blit(bg, camera)
    pygame.display.update()
    while a.rect.top > -SIZE*2:
        clock.tick(60)
        a.rect.left += 2
        a.rect.top -= 2
        #camera.update(a)
        full_blit(bg, camera)
        pygame.display.update()        
    #raise SystemExit
def main():
    pygame.init()
    l = [
       'N  Q                                       T',
       'TTTTT                        LLL           B',
       'B                       SS   LIL           B',
       'B                    TTTTTTTTTTT           B',
       'B                                          B',
       'B                                          B',
       'B     W                                    B',
       'B    TTTTTTTT                              B',
       'B                                          B',
       'B                   @      TTTTTTT         B',
       'B                 TTTTTT                   B',
       'B                                          B',
       'B         TTTTTTT                          B',
       'B                       M                  B',
       'B                     TTTTTT               B',
       'B   U   M                                  B',
       'B   TTTTTTTTTTT                            B',
       'B                                          B',
       'B                 TTTTTTTVVVT              B',
       'B                                          B',
       'B                                          B',
       'B                                      OOO B',
       'B                M                     OKO B',
       'BTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTAAATTTTB'
       ]
    run(l)
    print('You win!')
    raise SystemExit

main()
