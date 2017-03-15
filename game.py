import pygame
import os
from PIL import Image

global unlocked, entities, player1
player1 = None
entities = pygame.sprite.Group()
unlocked = []

WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

SIZE = 32
SPEED_SHIFT = SIZE/32

def load(image, size=(SIZE, SIZE), player=False):
    image = Image.open('resources/'+image)
    if player:
        size = (SIZE, SIZE*2)
    return pygame.transform.smoothscale(pygame.image.fromstring(image.tobytes(), image.size, image.mode), size)

images = {
          'T' : load('top.png'),
          'B' : load('bottom.png'),
          'E' : load('door-closed-top.png'), 
          'F' : load('door-closed-bottom.png'), 
          'L' : load('lock-red.png'), 
          'K' : load('key-red.png'),
          'A' : load('lava.png'),
          'S' : load('spikes.png'),
         }

player_prefix = "alienBlue_"
player_load = lambda image: load(player_prefix + image, player=True)
player_images = {
                 'PWalk1': player_load('walk1.png'),
                 'PWalk2': player_load('walk2.png'),
                 'PJump': player_load('jump.png'),
                 'PFall': player_load('fall.png'),
                 'PIdle': player_load('idle.png'),
                }

solidTiles = {'P':True, ' ':False}
empty = [' ', '@']
deadly = ['A', 'S']
winners = ['E', 'F']
keys = {'K': 'L'}

screen = pygame.display.set_mode((800, 640), 0, 32)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Platform(Entity):
    def __init__(self, x, y, imag):
        Entity.__init__(self)
        self.image = imag
        self.rect = pygame.Rect(x, y, SIZE, SIZE//2)
        self.type = {v: k for k,v in images.items()}[imag]
        self.show = True

class Player(Entity):
    def __init__(self, x, y, level, speed):
        Entity.__init__(self)
        self.x = self.origX = x
        self.y = self.origY = y
        
        self.level = level

        self.max_speed = speed
        self.sx = 0
        self.sy = 0
        
        self.onGround = False
        self.rect = pygame.Rect(x, y, SIZE, SIZE*2)
        self.frame = 1
        self.frameset()

        self.won = False
        self.type = "Player"
        self.show = True

    def run(self, up, left, right):
        #movement
        if up and self.onGround:
            self.sy = -11 * SPEED_SHIFT
        if left:
            self.sx = -8 * SPEED_SHIFT
        elif right:
            self.sx = 8 * SPEED_SHIFT
        else:
            self.sx = 0

        #entropy
        if self.sx != 0:
            if self.sx < 0:self.sx += 0.03
            self.sx *= 0.75

        #gravity
        if not self.onGround:
            self.sy += 0.3 * SPEED_SHIFT

        self.rect.left += self.sx
        self.collide(self.sx, 0, self.level.platforms)

        self.rect.top += self.sy
        self.onGround = False
        self.collide(0, self.sy, self.level.platforms)
        
        if self.rect.top < 0:
            self.rect.top = self.sy = 0
            
        if self.rect.left < 0:
            self.rect.left = self.sx = 0
    
    def collide(self, sx, sy, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if p.type in deadly:
                    self.die()
                    
                elif p.type in winners:
                    self.won = True
                    
                elif p.type in keys:
                    unlock(keys[p.type])
                    unlock(p.type)
                    
                else:
                    if sx > 0:
                        self.rect.right = p.rect.left
                        
                    elif sx < 0:
                        self.rect.left = p.rect.right
                        
                    if sy > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.sy = 0
                        
                    elif sy < 0:
                        self.rect.top = p.rect.bottom
                        self.sy = 0
    def die(self):
        self.rect = pygame.Rect(self.x, self.y, SIZE, SIZE)
        self.sx = self.sy = 0
        
    def frameset(self):
        self.frame = -self.frame + 3 #1->2, 2->1
        if self.sy < 0:
            self.image = player_images['PJump']
        elif self.sy > 0 and self.sy not in [0.3, 0.6, 0.8999999999999999]:
            self.image = player_images['PFall']
        elif self.sx != 0:
            self.image = player_images[f'PWalk{self.frame}']
        else:
            self.image = player_images['PIdle']
        if self.sx < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        
        
class Level():
    def __init__(self, tile_width, tile_height, level):
        self.height = len(level)
        self.width = len(level[0])
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.level = level
        
    def start(self):
        self.platforms = []
        for ri, row in enumerate(self.level):
            for ci, col in enumerate(row):
                if col not in empty:
                    self.platforms.append(Platform(ci*self.tile_height, ri*self.tile_width, images[col]))

    def find(self, square):
        for ri, row in enumerate(self.level):
            for ci, col in enumerate(row):
                if col == square:
                    yield ci, ri
        
class Camera():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = pygame.Rect(0, 0, width, height)
        
    def camera(self, target_rect):
        l, t, _, _ = target_rect
        _, _, w, h = self.state
        l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

        l = min(0, l)                           # stop scrolling at the left edge
        l = max(-(self.state.width-WIN_WIDTH), l)   # stop scrolling at the right edge
        t = max(-(self.state.height-WIN_HEIGHT), t) # stop scrolling at the bottom
        t = min(0, t)                           # stop scrolling at the top
        return pygame.Rect(l, t, w, h)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera(target.rect)

def destroy(e):
    e.show = False
    e.rect.width=0
    e.rect.height=0
    
def unlock(_type, platforms=entities, rep=' '):
    for i in platforms:
        if i.type == _type:
            destroy(i)

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
                    
        # draw background
        for y in range(SIZE):
            for x in range(SIZE):
                screen.blit(bg, (x * SIZE, y * SIZE))
                
        player1.run(up, left, right)
        camera.update(player1)
        
        for e in entities:
            if e.show:
                screen.blit(e.image, camera.apply(e))
        if i % 3/SPEED_SHIFT == 0:
            player1.frameset()
        i += 1
        pygame.display.update()
    
def main():
    pygame.init()
    l = [
       '                             LLL           T',
       'T                            LEL           B',
       'B                       SS   LFL           B',
       'B                    TTTTTTTTTTT           B',
       'B                                          B',
       'B                                          B',
       'B                                          B',
       'B    TTTTTTTT                              B',
       'B                                          B',
       'B                   @      TTTTTTT         B',
       'B                 TTTTTT                   B',
       'B                                          B',
       'B         TTTTTTT                          B',
       'B                                          B',
       'B                     TTTTTT               B',
       'B                                          B',
       'B   TTTTTTTTTTT                            B',
       'B                                          B',
       'B                 TTTTTTTTTTT              B',
       'B                                          B',
       'B                                          B',
       'B                                          B',
       'B                                       K  B',
       'BTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTAAATTTTB'
       ]
    run(l)
    print('You win!')
    raise SystemExit

main()



