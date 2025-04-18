import pygame
import sys
import math

pygame.init()

TILE_SIZE = 50
SCREEN_WIDTH = TILE_SIZE*15
SCREEN_HEIGHT = TILE_SIZE*11

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# starting point of top left corner of square
CENTRE_SCREEN = [SCREEN_WIDTH/2 - TILE_SIZE/2, SCREEN_HEIGHT/2 - TILE_SIZE/2]

player = pygame.Rect((CENTRE_SCREEN[0], CENTRE_SCREEN[1], TILE_SIZE, TILE_SIZE))
r, g, b = 0, 0, 255 # starting colour
colour_direction = 1 # 1 for up, -1 for down

# for the grid
dot_colour = (0, 255, 128)  # retro greenish-cyan
dot_radius = 2

def update_color(r, g, b):
    speed = 2
    if r == 255 and g < 255 and b == 0:
        g += speed
    elif g == 255 and r > 0:
        r -= speed
    elif g == 255 and b < 255:
        b += speed
    elif b == 255 and g > 0:
        g -= speed
    elif b == 255 and r < 255:
        r += speed
    elif r == 255 and b > 0:
        b -= speed
    return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

run = True
can_move = True

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if event.type == pygame.KEYDOWN and can_move:
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] == True:
            player.move_ip(-TILE_SIZE,0)
            can_move = False
        elif key[pygame.K_RIGHT] == True: # using elif instead of if prevents player moving in two directions in one go
            player.move_ip(TILE_SIZE,0)
            can_move = False
        elif key[pygame.K_UP] == True:
            player.move_ip(0,-TILE_SIZE)
            can_move = False
        elif key[pygame.K_DOWN] == True:
            player.move_ip(0,TILE_SIZE)
            can_move = False

    if player.left < 0:
        player.left = 0 
    if player.right > SCREEN_WIDTH:
        player.right = SCREEN_WIDTH 
    if player.top < 0:
        player.top = 0 
    if player.bottom > SCREEN_HEIGHT:
        player.bottom = SCREEN_HEIGHT 

    if event.type == pygame.KEYUP:
        can_move = True

    screen.fill((0,0,0)) # resets the screen to black

    # draws grid
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.circle(screen, dot_colour, (x, y), dot_radius)
    
    r, g, b = update_color(r, g, b)

    # draw a black square, shrink the coloured square, then draw it in inside the black square
    #pygame.draw.rect(screen, (100, 100, 100), player)
    #inner_rect = player.inflate(-4, -4)
    #pygame.draw.rect(screen, (r, g, b), inner_rect)
    pygame.draw.rect(screen, (r, g, b), player)

    pygame.display.update()
    clock.tick(90) # 60 frames per second

pygame.quit()
sys.exit()
