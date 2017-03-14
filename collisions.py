
def check_collision(obj1,obj2):
    """checks if two objects have collided, using hitmasks"""
    try:rect1, rect2, hm1, hm2 = obj1.rect, obj2.rect, obj1.hitmask, obj2.hitmask
    except AttributeError:return False
    rect=rect1.clip(rect2)
    if rect.width==0 or rect.height==0:
        return False
    x1,y1,x2,y2 = rect.x-rect1.x,rect.y-rect1.y,rect.x-rect2.x,rect.y-rect2.y
    for x in range(rect.width):
        for y in range(rect.height):
            if hm1[x1+x][y1+y] and hm2[x2+x][y2+y]:return True
            else:continue
    return False

def get_colorkey_hitmask(image, rect, key=None):
    """returns a hitmask using an image's colorkey.
       image->pygame Surface,
       rect->pygame Rect that fits image,
       key->an over-ride color, if not None will be used instead of the image's colorkey"""
    if key==None:colorkey=image.get_colorkey()
    else:colorkey=key
    mask=[]
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not image.get_at((x,y)) == colorkey)
    return mask

def get_alpha_hitmask(image, rect, alpha=0):
    """returns a hitmask using an image's alpha.
       image->pygame Surface,
       rect->pygame Rect that fits image,
       alpha->the alpha amount that is invisible in collisions"""
    mask=[]
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not image.get_at((x,y))[3]==alpha)
    return mask

def get_colorkey_and_alpha_hitmask(image, rect, key=None, alpha=0):
    """returns a hitmask using an image's colorkey and alpha."""
    mask=[]
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not (image.get_at((x,y))[3]==alpha or\
                                image.get_at((x,y))==key))
    return mask

def get_full_hitmask(image, rect):
    """returns a completely full hitmask that fits the image,
       without referencing the images colorkey or alpha."""
    mask=[]
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(True)
    return mask

def pixelPerfectCollision(obj1, obj2):
    #true-collision https://www.pygame.org/wiki/FastPixelPerfect
    try:
        #create attributes
        rect1, mask1, blank1 = obj1.rect, obj1.hitmask, obj1.blank
        rect2, mask2, blank2 = obj2.rect, obj2.hitmask, obj2.blank
        #initial examination
        if rect1.colliderect(rect2) is False:
            return False
    except AttributeError:
        print('i am a horbail haom')
        return False

    #get the overlapping area
    clip = rect1.clip(rect2)

    #find where clip's top-left point is in both rectangles
    x1 = clip.left - rect1.left
    y1 = clip.top  - rect1.top
    x2 = clip.left - rect2.left
    y2 = clip.top  - rect2.top

    #cycle through clip's area of the hitmasks
    for x in range(clip.width):
        for y in range(clip.height):
            #returns True if neither pixel is blank
            if mask1[x1+x][y1+y] is not blank1 and \
               mask2[x2+x][y2+y] is not blank2:
                return True

    #if there was neither collision nor error
    return False 

def vadd(x,y):
    return [x[0]+y[0],x[1]+y[1]]

def vsub(x,y):
    return [x[0]-y[0],x[1]-y[1]]

def vdot(x,y):
    return x[0]*y[0]+x[1]*y[1]

def collision_normal(left_mask, right_mask, left_pos, right_pos):


    offset = map(int,vsub(left_pos,right_pos))

    overlap = left_mask.overlap_area(right_mask,offset)

    if overlap == 0:
        return None, overlap

    """Calculate collision normal"""

    nx = (left_mask.overlap_area(right_mask,(offset[0]+1,offset[1])) -
          left_mask.overlap_area(right_mask,(offset[0]-1,offset[1])))
    ny = (left_mask.overlap_area(right_mask,(offset[0],offset[1]+1)) -
          left_mask.overlap_area(right_mask,(offset[0],offset[1]-1)))
    if nx == 0 and ny == 0:
        """One sprite is inside another"""
        return None, overlap

    n = [nx,ny]

    return n, overlap
