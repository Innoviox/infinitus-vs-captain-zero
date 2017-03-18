import pygame
from PIL import Image

SIZE = 32
SPEED_SHIFT = SIZE/32

def load(image, size=(SIZE, SIZE), player=False):
    image = Image.open('resources/'+image)
    if player:
        size = (SIZE, SIZE*2)
    return pygame.transform.smoothscale(pygame.image.fromstring(image.tobytes(), image.size, image.mode), size)

images = {
          'A' : load('lava.png'),
          'B' : load('bottom.png'),
          'E' : load('door-closed-top.png'), 
          'F' : load('door-closed-bottom.png'),
          'G' : load('door-open-top.png'),
          'H' : load('door-open-bottom.png'),
          'I' : load('ship-blue.png'),
          'J' : load('ship-blue-manned.png', size=(SIZE*2,SIZE*2)),
          'K' : load('key-red.png'),
          'L' : load('lock-red.png'),
          'M1': load('slime1.png'),
          'M2': load('slime2.png'),
          'N' : load('key-blue.png'),
          'O' : load('lock-blue.png'),
          'P1': load('lever1.png'),
          'P2': load('lever2.png'),
          'P3': load('lever3.png'),
          'Q1': load('fence.png'),
          'Q2': load('fenceBroken.png'),
          'R' : load('metalHalf.png'),
          'S' : load('spikes.png'),
          'T' : load('top.png'),
          'U1': load('switchBlue1.png'),
          'U2': load('switchBlue2.png'),
          'V1': load('grassEnemy.png'),
          'W1': load('spider2.png'),
          'W2': load('spider3.png'),
          #'W3': load('spider3.png'),
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
fences = ['Q', ['0', '1'], ['2']] #[type, [closed], [open]]
enemies = ['M', 'M1', 'M2', 'V', 'W']
enemy_attr_dict = {
                   'M': [2, 17, 5, True],
                   'V': [0, 0, 0, False],
                   'W': [2, 25, 5, True],
                  }
