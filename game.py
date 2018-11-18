import pygame
import os
import time
import random
import numpy as np
import sys
from PIL import Image

global unlocked, entities, player1, moved, playerdied, zero_func
moved = None
player1 = None
entities = pygame.sprite.Group()
unlocked = []
playerdied = False
zero_func = None

WIN_WIDTH = 800  # 1280
WIN_HEIGHT = 640  # 800
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), 0, 32)

pygame.font.init()
font = pygame.font.SysFont("monospace", 24)
bigfont = pygame.font.SysFont("monospace", 144)
clock = pygame.time.Clock()

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
    'A': load('lava.png'),
    'B': load('bottom.png'),
    'E': load('door-closed-top.png'),
    'F': load('door-closed-bottom.png'),
    'G': load('door-open-top.png'),
    'H': load('door-open-bottom.png'),
    'I': load('ship-blue.png'),
    'J': load('ship-blue-manned.png', size=(SIZE*2, SIZE*2)),
    'K': load('key-red.png'),
    'L': load('lock-red.png'),
    'M1': load('slime1.png'),
    'M2': load('slime2.png'),
    'N': load('key-blue.png'),
    'O': load('lock-blue.png'),
    'P1': load('lever1.png'),
    'P2': load('lever2.png'),
    'P3': load('lever3.png'),
    'Q1': load('fence.png'),
    'Q2': load('fenceBroken.png'),
    'R': load('metalHalf.png'),
    'S': load('spikes.png'),
    'T': load('top.png'),
    'U1': load('switchBlue1.png'),
    'U2': load('switchBlue2.png'),
    'V1': load('grassEnemy.png'),
    'W1': load('spider2.png'),
    'W2': load('spider3.png'),
    # 'W3': load('spider3.png'),
    'E1': load('bam1.png', size=(400, 400)),
    'E2': load('bam2.png', size=(800, 640)),
    'E3': load('bam3.png', size=(400, 400)),
    'E4': load('bam4.png', size=(400, 400)),
    'Z':  load('evil-in-its-raw-form.png'),
}

player_prefix = "infinity_"


def player_load(image): return load(player_prefix + image, player=True)


player_images = {
    'PWalk1': player_load('walk1.png'),
    'PWalk2': player_load('walk2.png'),
    'PJump': player_load('jump.png'),
    'PFall': player_load('fall.png'),
    'PIdle': player_load('idle.png'),
}

empty = [' ', '@']
deadly = ['A', 'S']
winners = ['E', 'F', 'I']
keys = {'K': 'L', 'N': 'O'}

movings = {'P': 'Q', 'U': 'Q'}
changing_attr_dict = {
    'P': [3],
    'Q': [2],
    'U': [2],
}
changers = ['P', 'Q', 'U']
fences = ['Q', ['0', '1'], ['2']]  # [type, [closed], [open]]
enemies = ['M', 'M1', 'M2', 'V', 'W']
enemy_attr_dict = {
    'M': [2, 17, 5, True],
    'V': [0, 0, 0, False],
    'W': [2, 25, 5, True],
}


class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class Platform(Entity):
    def __init__(self, x, y, imag, size=SIZE):
        Entity.__init__(self)
        self.image = imag
        self.rect = pygame.Rect(x, y, size, size//2)
        self.type = {v: k for k, v in images.items()}[imag]
        self.show = True
        self.x = x
        self.y = y
        if self.type == 'J':
            self.rect = pygame.Rect(x, y-size, size, size//2)
        self.frame = 0


class Changing(Platform):
    def __init__(self, x, y, imag, frames):
        Platform.__init__(self, x, y, images[imag+'1'])
        self.type = self.type[0]
        self.frame = 0
        self.frames = frames

    def check(self):
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
        self.x += random.randint(-(self.m//2)*self.change,
                                 (self.m//2)*self.change)
        # self.fall()

    def animate(self):  # , platforms):
        self.i += 1
        if self.mc:
            self.frameset()
            self.sx = self.change
            self.run()
            if self.i % self.d == 0:
                self.change = -self.change

        else:
            global player1
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

    def run(self):
        self.rect.left += self.sx

    def fall(self):
        while not self.onGround:
            self.run()

    def collide(self, sx, sy, platforms):
        for p in platforms:
            if not p is self:
                if pygame.sprite.collide_rect(self, p):
                    if p.type in deadly:
                        global playerdied
                        playerdied = True
                        p.image = images['Z']
                        p.show = True

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

    def run(self, up, left, right):
        # movement
        if up and self.onGround:
            self.sy = -11 * SPEED_SHIFT
        if left:
            self.sx = -8 * SPEED_SHIFT
        elif right:
            self.sx = 8 * SPEED_SHIFT
        else:
            self.sx = 0

        # entropy
        if self.sx != 0:
            if self.sx < 0:
                self.sx += 0.03
            self.sx *= 0.75

        # gravity
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
                global playerdied
                if p.type in deadly:
                    playerdied = True
                    p.image = images['Z']
                    p.show = True

                elif p.type in winners:
                    self.won = True

                elif p.type in keys:
                    unlock(keys[p.type])
                    unlock(p.type)

                elif p.type[0] in enemies:
                    playerdied = True
                    p.image = images['Z']
                    p.show = True
                elif p.type[0] in movings.keys():
                    global moved
                    moved = [p.type, movings[p.type[0]]]

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
        self.frame = -self.frame + 3  # 1->2, 2->1
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

    def create_platform(self, ci, ri, _type):
        return Platform(ci*self.tile_height, ri*self.tile_width, _type)

    def create_enemy(self, ci, ri, _type):
        return Enemy(ci*self.tile_height, ri*self.tile_width, _type, *enemy_attr_dict[_type])

    def create_mover(self, ci, ri, _type):
        return Changing(ci*self.tile_height, ri*self.tile_width, _type, *changing_attr_dict[_type])

    def start(self):
        self.platforms = []
        self.enemies = []
        self.movers = []
        for ri, row in enumerate(self.level):
            for ci, col in enumerate(row):
                if col not in empty:
                    if col in enemies:
                        self.enemies.append(self.create_enemy(ci, ri, col))
                    elif col in changers:
                        self.movers.append(self.create_mover(ci, ri, col))
                    else:
                        self.platforms.append(
                            self.create_platform(ci, ri, images[col]))
        self.platforms.extend(self.movers)

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

        # stop scrolling at the left edge
        l = min(0, l)
        # stop scrolling at the right edge
        l = max(-(self.state.width-WIN_WIDTH), l)
        # stop scrolling at the bottom
        t = max(-(self.state.height-WIN_HEIGHT), t)
        t = min(0, t)                           # stop scrolling at the top
        return pygame.Rect(l, t, w, h)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera(target.rect)


def destroy(e):
    e.show = False
    e.rect.width = e.rect.height = 0
    e.rect.top = e.rect.left = 1923781470398


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

    global moved, entities
    if moved is not None:
        for e in entities:
            if isinstance(e, Changing):
                e.check()
    for e in entities:
        if e.show:
            screen.blit(e.image, camera.apply(e))


def render_function(f):
    e, n = str(f).split("\n")
    for i in e, "", n:
        yield font.render(i, 1, (255, 255, 255))


def run(l, function):
    level = Level(SIZE, SIZE, l)
    level.start()

    p1 = next(level.find('@'))
    global player1
    player1 = Player(p1[0]*SIZE, p1[1]*SIZE, level, 5)

    bg = pygame.Surface((SIZE, SIZE))
    bg.convert()
    bg.fill(pygame.Color("#000000"))

    global entities
    for p in level.platforms:
        entities.add(p)
    for e in level.enemies:
        entities.add(e)
    for e in level.movers:
        entities.add(e)
    entities.add(player1)

    total_level_width = len(level.level[0])*SIZE
    total_level_height = len(level.level)*SIZE
    camera = Camera(total_level_width, total_level_height)
    up = left = right = False
    i = 0
    # p4 = gen_func()
    f = function
    dead_i = 0
    k = 0
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
        global playerdied
        if playerdied:
            pygame.event.get()
            full_blit(bg, camera)
            if dead_i == 0:
                dead_i = 1
            else:
                dead_i += 1
            if dead_i >= 10:
                screen.blit(bigfont.render("OH", 1, (255, 0, 0)), (200, 100))
            if dead_i >= 30:
                screen.blit(bigfont.render("NO", 1, (255, 0, 0)), (500, 100))
            if dead_i > 60:
                battle(f)
        else:
            player1.run(up, left, right)

            camera.update(player1)

            if i % 3/SPEED_SHIFT == 0:
                player1.frameset()
            if i % 6/SPEED_SHIFT == 0:
                for e in level.enemies:
                    e.animate()
            i += 1

            full_blit(bg, camera)
            for __i, __k in enumerate(render_function(f)):
                screen.blit(__k, (0, __i*10))
            k += 1
        pygame.display.update()

    for (i, p) in enumerate(level.platforms):
        if p.type == 'I':
            t = (i, p)
    a = Platform(t[1].x, t[1].y, images['J'])
    level.platforms[t[0]] = a
    entities.remove(t[1])
    entities.add(a)
    full_blit(bg, camera)
    pygame.display.update()

    player1.fall()
    player1.frameset()
    destroy(player1)
    full_blit(bg, camera)
    pygame.display.update()
    while a.rect.top > -SIZE*2:
        clock.tick(60)
        a.rect.left += 2
        a.rect.top -= 2
        full_blit(bg, camera)
        pygame.display.update()


def battle(f, start=True):
    def render_functions():
        (ei, ni), (ez, nz) = str(f).split("\n"), str(zero_func).split("\n")
        l = max(len(ni), len(nz))

        a = len(ni)
        while len(ni) < (l + a) / 2:
            ni = " " + ni
            ei = " " + ei

        a = len(nz)
        while len(nz) < (l + a) / 2:
            nz = " " + nz
            ez = " " + ez

        text = ("\n\n\n" +
                "        " + ei + "\n" +
                "  lim   " + ni + "\n" +
                "        " + "-" * l + "\n" +
                "        " + ez + "\n" +
                " x -> ∞ " + nz)
        return text
    text = ("Aha! You have found the infamous Captain Zero!\n"
            "\n\n\n              To battle!\n"
            "\n\n\n         Click to continue. ")
    if start:
        render_text(text)  # , clickable=False)
    global zero_func
    if not zero_func:
        zero_func = gen_func()
    while len(f.c) > 1 and len(zero_func.c) > 1:
        text = ("Your mightiness is:\n" + str(f) +
                "\n\n\nCaptain Zero's mightiness is:\n" + str(zero_func) +
                "\n\n\n        It's a BATTLE!")
        render_text(text)  # , clickable=False)
        _t = render_functions()
        render_text(_t, staggered=False)

        t = 0
        while t < 10:
            pygame.event.get()
            bam = Platform(50, 50, images['E' + str(random.randint(2, 2))])
            screen.blit(bam.image, (0, 0))
            t += 1
            time.sleep(0.01 - (t/10000))
            pygame.display.update()
        f = np.polyder(f)
        zero_func = np.polyder(zero_func)
        _t += "\n\n\n\n\n\n" + "=".center(len(_t.split("\n")[5])) + "\n\n\n"
        _t += render_functions()
        render_text(_t, staggered=False)

    i_died, z_died = len(f.c) == 1, len(zero_func.c) == 1
    text = ("Your mightiness is:\n" + str(f) +
            "\n\n\nCaptain Zero's mightiness is:\n" + str(zero_func) +
            "\n\n\n")
    render_text(text, staggered=False)  # , clickable=False)
    if i_died and z_died:
        final = f.c[0] / zero_func.c[0]
        text += ("\n\nYou have fought each other to the death!\n"
                 f"Final score: {final}\n"
                 "Good game! ")
        render_text(text, staggered=False)
    elif z_died:
        i = f(123567654321234567)
        z = zero_func(123567654321234567)
        if i / z < 0:
            text += ("\n\nYou have valiantly defeated the evil Captain Zero!\n"
                     "But in doing so, you went to the dark side.\n"
                     "The limit has gone to -∞!\n"
                     "Game over! ")
        else:
            text += ("\n\nYou have valiantly defeated the evil Captain Zero!\n"
                     "The limit has gone to ∞!\n"
                     "Game over! ")
        render_text(text, staggered=False)
    else:
        text += ("\n\nThe evil Captain Zero has evilly defeated you.\n"
                 "The limit has gone to 0.\n"
                 "Game over. ")
        render_text(text, staggered=False)
    sys.exit(0)


def gen_func(min_=1, max_=4):
    return np.poly1d(np.polyfit(np.random.rand(6), np.random.rand(6), random.randint(min_, max_)))


def render_text(t, clickable=True, staggered=True):
    rendered_texts = [""]
    t = list(t)[:]
    rendering = staggered
    while t:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and clickable:
                rendering = False
        s = t.pop(0)
        if s == "\n":
            rendered_texts.append("")
            rendered_texts.append("")
        else:
            rendered_texts[-1] += s
        if rendering:
            label = [font.render(i, 1, (255, 255, 255))
                     for i in rendered_texts]

            screen.fill((0, 0, 0))
            for j, k in enumerate(label):
                screen.blit(k, (0, j*10))
            pygame.display.flip()

    clicked = False
    while not clicked:
        evs = pygame.event.get()
        for event in evs:
            if event.type == pygame.MOUSEBUTTONUP:
                clicked = True

        label = [font.render(i, 1, (255, 255, 255)) for i in rendered_texts]
        screen.fill((0, 0, 0))
        for j, k in enumerate(label):
            screen.blit(k, (0, j*10))
        pygame.display.flip()


def storyline():
    func = gen_func()
    exp, f = str(func).split("\n")
    full_intro = ("You are Infinitus. Hailing from a distant galaxy, you\n"
                  "have come to defeat the evil Captain Zero once and for\n"
                  "all. Unfortunately you cannot breathe on his planet so\n"
                  "you must wear a helmet. When you arrived, you did not\n"
                  "find him and so chose to run back to your ship and \n"
                  "come again another day. Get to your ship! \n"
                  "Your current mightiness is:\n" +
                  exp + "\n" + f + " " +
                  "\n\n\n         Click to continue. ")
    render_text(full_intro)
    return func


def intro():
    func = gen_func()
    p4 = str(func).split("\n")
    label = [font.render("              Your Mightiness Is:", 1, (255, 0, 0)),
             font.render("", 1, (255, 0, 0))]
    for j, i in enumerate(p4):
        label.append(font.render(i, 1, (255, 0, 0)))
    t = 0
    while t < 10000:
        screen.fill((255, 255, 255))
        pygame.event.get()
        for j, k in enumerate(label):
            screen.blit(k, (0, j*10))
        pygame.display.flip()
        t += 60
    return func


def win(f):
    text = ("You have successfully escaped the planet\n"
            "of the evil Captain Zero! ")
    # render_text(text)
    # time.sleep(1)
    text += ("                             \n              \n\n\n\n\nWhoa! On exiting orbit you have found\n"
             "the evil captain zero has set an evil trap!\n"
             "He must be defeated once and for all!")
    render_text(text, clickable=False)
    battle(f, start=False)


def main():
    pygame.init()
    l = [
        '   Q                                       T',
        'N  T                         LLL           B',
        'TTTBT                   SS   LIL           B',
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
        'B                 TTTTTTTTTTT              B',
        'B                                          B',
        'B                                          B',
        'B                                      OOO B',
        'B                M                     OKO B',
        'BTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTAAATTTTB'
    ]
    func = storyline()
    run(l, func)
    win(func)
    raise SystemExit


main()
