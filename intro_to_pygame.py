
""" Libraries """
import pygame
import sys
import math
import random

#############################################################################################################################################

pygame.init() # initialises modules

""" Global variables """
TILE_SIZE = 50
SCREEN_WIDTH = TILE_SIZE*15
SCREEN_HEIGHT = TILE_SIZE*11
PANEL_WIDTH = TILE_SIZE*5

screen = pygame.display.set_mode((SCREEN_WIDTH + PANEL_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

CENTRE_SCREEN = [SCREEN_WIDTH/2 - TILE_SIZE/2, SCREEN_HEIGHT/2 - TILE_SIZE/2] # starting coordinate of top left corner of square

player = pygame.Rect((CENTRE_SCREEN[0], CENTRE_SCREEN[1], TILE_SIZE, TILE_SIZE))
r, g, b = 0, 0, 255 # starting colour
colour_direction = 1 # 1 for up, -1 for down

dot_colour = (0, 255, 128)  # retro green
dot_radius = 2

font = pygame.font.SysFont("Courier", 20, bold=True)
title_font = pygame.font.SysFont("Courier", 28, bold=True)

guesses = []
feedback = []
sequence = [random.choice(['↑', '↓', '→', '←']) for x in range(4)]
dict = {'↑':0, '↓':0, '→':0, '←':0}
for i in sequence:
    dict[i] +=1
print(sequence)


""" Function to fade the colour of the playing square """
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

""" Function to draw the mastermind panel that tracks goes """
def draw_mastermind_panel(screen, guesses, feedback):
    panel_x = SCREEN_WIDTH # panel x is the game panel  
    screen.fill((20, 20, 20), (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))  # side panel colour
    
    # Title
    title_surf = title_font.render("Mastermove", True, (0, 250, 180))
    screen.blit(title_surf, (panel_x + 20, 20)) # blit is block transfer. it takes two arguments, a surface and a coordinate (x,y).

    # Draw guess rows
    for i, guess in enumerate(guesses):
        y = 70 + i * 45
        guess_str = " ".join(guess)  # e.g., ↑ ↑ →
        #guess_surf = font.render(f"{i+1} {guess_str}", True, (0, 250, 180)) # option with number of guesses
        guess_surf = font.render(f"{guess_str}", True, (0, 250, 180))
        screen.blit(guess_surf, (panel_x + 20, y))

        peg_size = 7
        spacing = 2
        peg_x_start = panel_x + 180
        peg_y_start = y + 5

        ### ISSUE 1: feedback being generated immediately (and not randomly reordering). 
        # Draw feedback boxes (black/white squares)  
        for j, outcome in enumerate(feedback[i]): # enumerate loops through items in a list by index j
            row = j // 2
            col = j % 2
            cx = peg_x_start + col * (peg_size * 2 + spacing)
            cy = peg_y_start + row * (peg_size * 2 + spacing)

            colour_rgb = (0, 0, 0) if outcome == 'miss' else (191, 0, 255) if outcome == 'wrong' else (0, 250, 180)
            
            pygame.draw.circle(screen, colour_rgb, (cx, cy), peg_size)
            pygame.draw.circle(screen, (50, 50, 50), (cx, cy), peg_size, 1) # faint border

def add_item(item, lst):
    if not lst or len(lst[-1]) == 4:
        lst.append([item])  # start a new sublist
    else:
        lst[-1].append(item)  # add to the last sublist

def response(lst):
    guess = lst[-1][-1]
    index = len(lst[-1]) -1
    if guess == sequence[index]:
        dict[guess] -= 1
        return 'correct'
    elif dict[guess] != 0: ### ISSUE 2: dict isn't being reset for each guess of 4 so we're getting reds where there should be blues. 
        dict[guess] -= 1
        return 'wrong'
    else:
        return 'miss'

#############################################################################################################################################

run = True
can_move = True

""" Game play """
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    """ Arrow keys for moving player """
    if event.type == pygame.KEYDOWN and can_move:
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] == True:
            player.move_ip(-TILE_SIZE,0)
            can_move = False
            add_item('←', guesses)
            add_item(response(guesses),feedback)
        elif key[pygame.K_RIGHT] == True: # using elif instead of if prevents player moving in two directions in one go
            player.move_ip(TILE_SIZE,0)
            can_move = False
            add_item('→', guesses)
            add_item(response(guesses),feedback)
        elif key[pygame.K_UP] == True:
            player.move_ip(0,-TILE_SIZE)
            can_move = False
            add_item('↑', guesses)
            add_item(response(guesses),feedback)
        elif key[pygame.K_DOWN] == True:
            player.move_ip(0,TILE_SIZE)
            can_move = False
            add_item('↓', guesses)
            add_item(response(guesses),feedback)


    """ Screen boundary """
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

    """ Screen background """
    screen.fill((0,0,0)) # resets the screen to black

    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.circle(screen, dot_colour, (x, y), dot_radius) # draws grid of dots
    
    r, g, b = update_color(r, g, b)

    """ Border on playing square """
    #pygame.draw.rect(screen, (100, 100, 100), player)
    #inner_rect = player.inflate(-4, -4)
    #pygame.draw.rect(screen, (r, g, b), inner_rect)

    pygame.draw.rect(screen, (r, g, b), player)

    draw_mastermind_panel(screen, guesses, feedback)
    pygame.display.update()# most important line
    clock.tick(90) # frames per second

pygame.quit()
sys.exit()

########################################################################################################################################################################
