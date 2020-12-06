#Program Variable all lowercase except for Window sizing Variable
#Class has Caps at the start of each word
#List has a (variable name if unique) or (if not the put L at the end)
#e.g Size(unqiue) or Running_SpeedL (common)
''' 
Important Stuff to know
---------------------------------------------------------------------------------------
X axis is normal going left -> right
Y axis is Inverted going top -> bottom
so 0,0 will be Top Left corner
---------------------------------------------------------------------------------------
SCREEN_VARIABLE.blit(surface/image, (xpos, ypos))
Path finding if in another Folder (FOLDER_NAME/item)
pygame.Rect(xpos, ypos, width, height)
pygame.draw.rect(SCREEN_VARIAVLE, RGBCODE(255,255,255), RECT_VARIABLE)
IMAGE_VARIABLE.set_colorkey(RGB(255, 255, 255))
RECT_VARIABLE.colliderect(OTHER_RECT_TILE)
---------------------------------------------------------------------------------------
'''
import pygame
import sys, os
from random import choice, randint
from math import floor, ceil
from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    K_w,
    K_a,
    K_s,
    K_d,
    K_m
)
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init() #initiate Pygames
pygame.mixer.set_num_channels(64)
#Functions/Classes
def collision_test(rect, rectL):
    hit_list = []
    for tile in rectL:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

def generating_chunks(x,y):
    chunk_data = []
    chunk_size = 8
    for y_pos in range(chunk_size):
        for x_pos in range(chunk_size):
            target_x = x * chunk_size + x_pos
            target_y = y * chunk_size + y_pos
            tile_type = 0 # air
            if target_y > 10:
                tile_type = 2 # dirt
            elif target_y == 10:
                tile_type = 1 # grass
            elif target_y == 9:
                if randint(1,5) == 1:
                    tile_type = 3 # plant
            if tile_type != 0:
                chunk_data.append([[target_x,target_y], tile_type])
    return chunk_data


global animation_frames
animation_frames = {}

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


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


#Window Stuff
Screen_Width = 300
Screen_Height = 200
Window_Size = (900, 600) #x,y
pygame.display.set_caption("My Pygame Window") #Set the Caption Window Like 'Terraria: Also Try Minecraft'
org_screen = pygame.display.set_mode(Window_Size, 0, 32)
screen = pygame.Surface((Screen_Width, Screen_Height))

#Image
dirt_image = pygame.image.load('dirt.png')
grass_image = pygame.image.load('grass.png')
plant_image = pygame.image.load('plant.png').convert()
plant_image.set_colorkey((255,255,255))
animation_database = {}
animation_database['run'] = load_animations('player_animations/run', [7, 7])
animation_database['idle'] = load_animations('player_animations/idle', [7, 7, 40])
tile_index = {
    1:grass_image,
    2:dirt_image,
    3:plant_image
}

# Variables
moving_right = False
moving_left = False
player_y_momentum = 0
air_timer = 0
tile_size = 16 #the 16 came from the ammount of pixel of the tile LengthxWidth
game_map = {}
true_scroll = [0, 0]
background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]
player_action = 'idle'
player_frame = 0
player_flip = False
has_double_jump = False
chuck_size = 8
ammount_of_chunk_on_screen =[ceil(Screen_Width/(chuck_size*tile_size))+1, ceil(Screen_Height/(chuck_size*tile_size))+1]
 

#Rect
player_img_id = animation_database[player_action][player_frame]
player_image = animation_frames[player_img_id]
player_rect = pygame.Rect(50, 50, player_image.get_width(), player_image.get_height())
test_rect = pygame.Rect(100, 100, 100, 50)

#Sound
jump_sound = pygame.mixer.Sound('jump.wav')
grass_sound = [pygame.mixer.Sound('grass_0.wav'), pygame.mixer.Sound('grass_1.wav')]
grass_sound[0].set_volume(0.2)
grass_sound[1].set_volume(0.2)
music = pygame.mixer.music.load('music.wav')
play_music = True
grass_sound_timer = 0

clock = pygame.time.Clock()
program_running = True
while program_running: #Game Loop
    screen.fill((146, 244, 255))
    if grass_sound_timer > 0:
        grass_sound_timer -= 1
    
    
    true_scroll[0] += (player_rect.x - true_scroll[0] - 152) #(sprite_width+screen_width)//2
    true_scroll[1] += (player_rect.y - true_scroll[1] - 106)#(sprite_height+screen_height)//2
    scroll = list(map(int, true_scroll))
    pygame.draw.rect(screen, (7, 80, 75),pygame.Rect(0, 120, 300, 80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],
        background_object[1][1]-scroll[1]*background_object[0], background_object[1][2],
        background_object[1][3]
        )
        if background_object[0] == 0.5:
            pygame.draw.rect(screen, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(screen, (9, 91, 85), obj_rect)
    
    #Map Render goes here
    tile_rects = []
    for y in range(ammount_of_chunk_on_screen[1]):
        for x in range(ammount_of_chunk_on_screen[0]):
            target_x = x - 1 + int(round(scroll[0]/(chuck_size*tile_size)))
            target_y = y - 1 + int(round(scroll[1]/(chuck_size*tile_size)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generating_chunks(target_x, target_y)
            for tile in game_map[target_chunk]:
                screen.blit(tile_index[tile[1]], (tile[0][0]*tile_size-scroll[0], tile[0][1]*tile_size-scroll[1]))
                if tile[1] in [1,2]:
                    tile_rects.append(pygame.Rect(tile[0][0]*tile_size,tile[0][1]*tile_size, tile_size, tile_size))
            
    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if player_movement[0] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = False
    
    elif player_movement[0] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = True
    else:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    player_rect, collisions = move(player_rect, player_movement, tile_rects)
    if collisions['bottom'] or collisions['top']:
        player_y_momentum = 0
        if collisions['bottom']:
            air_timer = 0
            has_double_jump = False
            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    choice(grass_sound).play()
                    grass_sound_timer = 30

    else:
        air_timer += 1

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_image = animation_frames[player_img_id]
    screen.blit(pygame.transform.flip(player_image, player_flip, False), (player_rect.x  - scroll[0], player_rect.y  - scroll[1]))
    

    for event in pygame.event.get():
        if event.type == KEYDOWN: #if a key is pressed down
            if event.key == K_d:
                moving_right = True
            if event.key == K_a:
                moving_left = True
            if event.key == K_w:
                if air_timer < 6:
                    jump_sound.play()
                    player_y_momentum = -5
                elif not has_double_jump:
                    jump_sound.play()
                    player_y_momentum = -5
                    has_double_jump = True
                    
            if event.key == K_m:
                play_music = not play_music
                if play_music:
                    pygame.mixer.music.fadeout(1000)
                else:
                    pygame.mixer.music.play(-1)
        if event.type == KEYUP: # if a key is pressed up
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False
        elif event.type == QUIT:
            program_running = False

    surf = pygame.transform.scale(screen, Window_Size)
    org_screen.blit(surf, (0,0))
    pygame.display.update() #update the window to whatever the screen variable is
    clock.tick(60)



pygame.quit()
sys.exit()