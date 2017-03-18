import objects
import images
class Level():
    def __init__(self, tile_width, tile_height, level):
        self.height = len(level)
        self.width = len(level[0])
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.level = level

    def create_platform(self, ci, ri, _type):
        return objects.Platform(ci*self.tile_height, ri*self.tile_width, _type)
    def create_enemy(self, ci, ri, _type):
        return objects.Enemy(ci*self.tile_height, ri*self.tile_width, _type, *images.enemy_attr_dict[_type])
    def create_mover(self, ci, ri, _type):
        return objects.Changing(ci*self.tile_height, ri*self.tile_width, _type, *images.changing_attr_dict[_type])
    def start(self):
        self.platforms = []
        self.enemies = []
        self.movers = []
        for ri, row in enumerate(self.level):
            for ci, col in enumerate(row):
                if col not in images.empty:
                    if col in images.enemies:
                        self.enemies.append(self.create_enemy(ci, ri, col))
                    elif col in images.changers:
                        self.movers.append(self.create_mover(ci, ri, col))
                    else:
                        self.platforms.append(self.create_platform(ci, ri, images.images[col]))
        self.platforms.extend(self.movers)
        
    def find(self, square):
        for ri, row in enumerate(self.level):
            for ci, col in enumerate(row):
                if col == square:
                    yield ci, ri
