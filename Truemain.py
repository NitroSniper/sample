
import pygame
import sys, os
import engine as ENG
from math import ceil
from random import randrange,randint

from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    K_w,
    K_s,
    K_d,
    K_a
)
pygame.init()


global animation_frames
animation_frames = {}



class Box(object):
    def __init__(self, falling_boxes):   
        fallingCords = list(map(lambda parameter_list: parameter_list.rect.x, falling_boxes))
        print (fallingCords)     
        self.image = pygame.image.load('Box.png')
        while True:
            randox = randrange(0, 600, 32)
            if randox not in fallingCords:
                self.rect = pygame.Rect(randox, 20,
                                    self.image.get_width(),
                                    self.image.get_height())
                break
        self.y_momentum = randint(1,2)
        self.state = 'falling'
    def fall(self):
        self.rect.y += self.y_momentum


def load_animations(path, frames_duration):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frames_duration:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255, 255, 255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

#Window Stuff
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
WINDOW_SIZE = (900, 600) #x, y
pygame.display.set_caption("DodgeBox: Starting") 
#Set the Caption Window Like 'Terraria: Also Try Minecraft'
DISPLAY = pygame.display.set_mode(WINDOW_SIZE, 0, 32) #True Screen
SCREEN = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)) #Screen to Blit on other Screen
clock = pygame.time.Clock()


#Variable
TILE_SIZE = 32
moving_left = False
moving_right = False
Y_momentum = 0
player_flip = False
air_timer = 0
player_y_momentum = 0
jump = False
player_action = 'idle'
player_frame = 0
player_speed = 3
boxOnScreen = 16


#Images
global animation_database
animation_database = {}
animation_database['run'] = load_animations('player_animations/running', [10,10])
animation_database['idle'] = load_animations('player_animations/idle', [1,0])
ground_image = pygame.image.load('Ground.png') 
player_img_id = animation_database[player_action][player_frame]
player_image = animation_frames[player_img_id]


#Music
musicAndSound = True

#Game Stuff
ground_tiles = []
for n in range(ceil(SCREEN_WIDTH/TILE_SIZE)):
    ground_tiles.append(pygame.Rect(n*TILE_SIZE, 368, 32,32))
boxes = []


print (ground_tiles)
#Rect
player_rect = pygame.Rect(50, 50,
              player_image.get_width(),
              player_image.get_height())



program_running = True
while program_running:
    SCREEN.fill((224, 219, 211))
    #EVENTS
    for event in pygame.event.get():
        if event.type == KEYDOWN: #if a key is pressed down
            if event.key == K_d:
                moving_right = True
            elif event.key == K_a:
                moving_left = True
            elif event.key == K_w:
                    jump = True
        elif event.type == KEYUP: # if a key is pressed up
            if event.key == K_d:
                moving_right = False
            elif event.key == K_a:
                moving_left = False
            elif event.key == K_w:
                jump = False
        elif event.type == QUIT:
            program_running = False


    #tile rects
    falling_boxes = []
    for box in boxes:
        if box.state == 'falling':
            falling_boxes.append(box)
    if len(boxes) <= boxOnScreen:
        for n in range(boxOnScreen-len(boxes)):
            boxes.append(Box(falling_boxes))
    tile_rects = list(map(lambda x: x.rect, boxes)) + ground_tiles

    #GameLogic
    for box in boxes:
        Box.fall(box)
        if box.rect.y > 400:
            boxes.remove(box)
            falling_boxes.remove(box)
    player_movement = [0,0]
    if jump:
        if air_timer < 6:
            player_y_momentum = -5
            
    if moving_right:
        player_movement[0] += player_speed
    if moving_left:
        player_movement[0] -= player_speed
    player_y_momentum += 0.2
    if player_y_momentum > 5:
        player_y_momentum = 5
    player_movement[1] += int(player_y_momentum)
    
    if player_movement[0] > 0:
        player_action, player_frame = ENG.change_action(player_action, player_frame, 'run')
        player_flip = False
    
    elif player_movement[0] < 0:
        player_action, player_frame = ENG.change_action(player_action, player_frame, 'run')
        player_flip = True
    else:
        player_action, player_frame = ENG.change_action(player_action, player_frame, 'idle')

    player_rect, collisions = ENG.move(player_rect, player_movement, tile_rects)
    if collisions['top']:
        print ("Fuck")

    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_image = animation_frames[player_img_id]



    #Draw
    for n in ground_tiles:  SCREEN.blit(ground_image, (n.x, n.y))
    for n in boxes: SCREEN.blit(n.image, (n.rect.x, n.rect.y))
    SCREEN.blit(pygame.transform.flip(player_image, player_flip, False), (player_rect.x, player_rect.y))
    DISPLAY.blit(pygame.transform.scale(SCREEN, WINDOW_SIZE), (0,0))
    pygame.display.update() #update the window to whatever the screen variable is
    clock.tick(60)


print (animation_database)
pygame.quit()
sys.exit()
