from images import *
import random

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    def _mask(self):
        self.mask = pygame.mask.from_surface(self.image)
        
class Platform(Entity):
    def __init__(self, x, y, imag):
        Entity.__init__(self)
        self.image = imag
        self.rect = pygame.Rect(x, y, SIZE, SIZE//2)
        self.type = {v: k for k,v in images.items()}[imag]
        self.show = True
        self.x = x
        self.y = y
        if self.type == 'J':
            self.rect = pygame.Rect(x, y-SIZE, SIZE, SIZE//2)
        self.frame=0
        self._mask()
        
class Changing(Platform):
    def __init__(self, x, y, imag, frames):
        Platform.__init__(self, x, y, images[imag+'1'])
        self.type = self.type[0]
        self.frame=0
        self.frames = frames
    def check(self, moved):
        if self.type in moved:
            self.frame += 1
            if self.frame <= self.frames:
                self.image = images[self.type + str(self.frame)]

            
class Enemy(Platform):
    def __init__(self, x, y, imag, frameMax, distance, speed, movesConstantly):
        #assert imag in enemies
        Platform.__init__(self, x, y, images[imag+'1'])
        self.type = self.type[0]
        self.frame = 1
        self.sx = 0
        self.sy = 0
        self.change = speed
        self.i = 0
        self.d = distance
        self.m = frameMax
        self.fc = 1
        self.mc = movesConstantly
        self.onGround = False
        self.broadcasted = False
        self.x += random.randint(-(self.m//2)*self.change, (self.m//2)*self.change)
        #self.fall()
        
    def animate(self, player1):#, platforms):
        self.i += 1
        if self.mc:
            self.frameset()
            self.sx = self.change
            self.run()
            if self.i % self.d == 0:
                self.change = -self.change
                

        else:
            if pygame.sprite.collide_rect(self, player1):
                print('lololol')
                self.frame += 1
                self.broadcast()
                self.broadcasted = True

    def broadcast(self):
        if not self.broadcasted:
            global moved
            moved = movings[self.imag]
        
    def frameset(self):
        self.frame += self.fc
        if self.frame == self.m:
            self.fc = -1
        if self.frame == 1:
            self.fc = 1
        self.image = images[self.type+str(self.frame)]
        if self.sx > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        
    def run(self):#, platforms):
##        #entropy
##        if self.sx != 0:
##            if self.sx < 0:self.sx += 0.03
##            self.sx *= 0.75

##        #gravity
##        if not self.onGround:
##            self.sy += 0.3 * SPEED_SHIFT

        self.rect.left += self.sx
##        self.collide(self.sx, 0, platforms)
##
##        self.rect.top += self.sy
##        self.onGround = False
##        self.collide(0, self.sy, platforms)
##        
##        if self.rect.top < 0:
##            self.rect.top = self.sy = 0
##            
##        if self.rect.left < 0:
##            self.rect.left = self.sx = 0

    def fall(self):
        while not self.onGround:
            self.run()
            
    def collide(self, sx, sy, platforms):
        for p in platforms:
            if not p is self:
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
        self._mask()
        self.moved = []
        self.unlocked = []
        
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
        
        if self.rect.top < -SIZE:
            self.rect.top = -SIZE
            self.sy = 0
            
        if self.rect.left < 0:
            self.rect.left = self.sx = 0

    def fall(self):
        while not self.onGround:
            self.run(False, False, False)
            
    def collide(self, sx, sy, platforms):
        def __collide(p):
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
        def _collide(p):
            if pygame.sprite.collide_rect(self, p):
                if p.type in deadly:
                    self.die()
                    
                elif p.type in winners:
                    self.won = True
                    
                elif p.type in keys:
                    self.unlocked = [keys[p.type], p.type]
                    
                elif p.type[0] in enemies:
                    self.die()
                elif p.type[0] in movings.keys():
                    self.moved = [p.type, movings[p.type[0]]]

                else:
                    if p.type[0] in fences:
                        if str(p.frame) in fences[1]:
                            __collide(p)
                    else:
                        __collide(p)

        for p in platforms:
            _collide(p)
        for p in self.level.enemies:
            _collide(p)
    def die(self):
        self.rect = pygame.Rect(self.x, self.y, SIZE, SIZE*2)
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
