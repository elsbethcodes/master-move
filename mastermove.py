""" Libraries """
import pygame
import sys
import math
import random

#############################################################################################################################################

pygame.init() # initialises all pygame modules

""" Global variables """
TILE_SIZE = 50
SCREEN_WIDTH = TILE_SIZE*15
SCREEN_HEIGHT = TILE_SIZE*13
PANEL_WIDTH = TILE_SIZE*5
GOES = 12

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

""" Global lists """
guesses = []
feedback = []
sequence = [random.choice(['↑', '↓', '→', '←']) for x in range(4)]
#print(sequence) #check


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
    panel_x = SCREEN_WIDTH
    screen.fill((20, 20, 20), (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))  # Side panel background

    # Title
    title_surf = title_font.render("Mastermove", True, (0, 250, 180))
    screen.blit(title_surf, (panel_x + 20, 20))

    # Draw guess rows
    for i, guess in enumerate(guesses):
        y = 70 + i * 45
        guess_str = " ".join(guess)
        guess_surf = font.render(f"{i+1}  {guess_str}", True, (0, 250, 180))
        screen.blit(guess_surf, (panel_x + 20, y))

        # Only draw feedback if this guess has 4 arrows
        if len(guess) == 4 and i < len(feedback):
            peg_size = 7
            spacing = 2
            peg_x_start = panel_x + 180
            peg_y_start = y + 5

            for j, outcome in enumerate(feedback[i]):
                row = j // 2
                col = j % 2
                cx = peg_x_start + col * (peg_size * 2 + spacing)
                cy = peg_y_start + row * (peg_size * 2 + spacing)

                colour_rgb = (
                    (0, 0, 0) if outcome == 'miss'
                    else (191, 0, 255) if outcome == 'incorrect position'
                    else (0, 250, 180)
                )

                pygame.draw.circle(screen, colour_rgb, (cx, cy), peg_size)
                pygame.draw.circle(screen, (50, 50, 50), (cx, cy), peg_size, 1)

# add_item allows a move to be added to guesses, in a new sublist if this is the first guess or a a guess of 4 moves has been completed 
def add_item(item, lst):
    if not lst or len(lst[-1]) == 4:
        lst.append([item])  # start a new sublist
    else:
        lst[-1].append(item)  # add to the last sublist

def get_feedback(guess, solution):
    feedback = []
    temp_solution = solution.copy()
    temp_guess = guess.copy()

    # First pass – correct position and symbol
    for i in range(4):
        if temp_guess[i] == temp_solution[i]:
            feedback.append('correct')
            temp_solution[i] = None
            temp_guess[i] = None

    # Second pass – correct symbol, incorrect position
    for i in range(4):
        if temp_guess[i] is not None and temp_guess[i] in temp_solution:
            feedback.append('incorrect position')
            temp_solution[temp_solution.index(temp_guess[i])] = None
        elif temp_guess[i] is not None:
            feedback.append('miss')
    return feedback

# Skull setup
PIXEL_SIZE = 5
skull_sprite = [
    [0,1,1,1,1,1,0],
    [1,1,1,1,1,1,1],
    [1,0,1,1,1,0,1],
    [1,0,0,1,0,0,1],
    [1,1,1,1,1,1,1],
    [0,1,1,1,1,1,0],
    [0,1,0,1,0,1,0],
]
SKULL_MOVE_INTERVAL = 2000
skull_timer = pygame.time.get_ticks()
skull_tile = [0, 0]  # skull grid position (x, y)

def draw_skull(x, y, color=(255,255,255)):
    for row_idx, row in enumerate(skull_sprite):
        for col_idx, pixel in enumerate(row):
            if pixel:
                rect = pygame.Rect(
                    x + col_idx * PIXEL_SIZE,
                    y + row_idx * PIXEL_SIZE,
                    PIXEL_SIZE, PIXEL_SIZE
                )
                pygame.draw.rect(screen, color, rect)

#############################################################################################################################################

run = True
can_move = True
c = 0 # counter

""" Game play """
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Skull pixel position
    skull_px = skull_tile[0] * TILE_SIZE
    skull_py = skull_tile[1] * TILE_SIZE

    # Skull moves every 2 seconds toward player
    current_time = pygame.time.get_ticks()
    if current_time - skull_timer >= SKULL_MOVE_INTERVAL and can_move:
        skull_timer = current_time

        # Calculate direction
        dx = player.x - skull_tile[0] * TILE_SIZE
        dy = player.y - skull_tile[1] * TILE_SIZE

        if abs(dx) > abs(dy):
            skull_tile[0] += 1 if dx > 0 else -1
        elif dy != 0:
            skull_tile[1] += 1 if dy > 0 else -1

    """ Arrow keys for moving player """
    if event.type == pygame.KEYDOWN and can_move:
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] == True:
            player.move_ip(-TILE_SIZE,0)
            can_move = False # stops the playing square moving again for a sustained keypress
            add_item('←', guesses)
            if len(guesses[-1]) == 4:
                feedback.append(sorted(get_feedback(guesses[-1], sequence)))
            c+=1
        elif key[pygame.K_RIGHT] == True: # using elif instead of if prevents player moving in two directions in one go
            player.move_ip(TILE_SIZE,0)
            can_move = False
            add_item('→', guesses)
            if len(guesses[-1]) == 4:
                feedback.append(sorted(get_feedback(guesses[-1], sequence)))
            c+=1
        elif key[pygame.K_UP] == True:
            player.move_ip(0,-TILE_SIZE)
            can_move = False
            add_item('↑', guesses)
            if len(guesses[-1]) == 4:
                feedback.append(sorted(get_feedback(guesses[-1], sequence)))
            c+=1
        elif key[pygame.K_DOWN] == True:
            player.move_ip(0,TILE_SIZE)
            can_move = False
            add_item('↓', guesses)
            if len(guesses[-1]) == 4:
                feedback.append(sorted(get_feedback(guesses[-1], sequence)))
            c+=1

    """ Screen boundary """
    if player.left < 0:
        player.right = SCREEN_WIDTH
    elif player.right > SCREEN_WIDTH:
        player.left = 0
    if player.top < 0:
        player.bottom = SCREEN_HEIGHT
    elif player.bottom > SCREEN_HEIGHT:
        player.top = 0

    if event.type == pygame.KEYUP:
        can_move = True


    """ Screen background """
    screen.fill((0,0,0)) # resets the screen to black

    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.circle(screen, dot_colour, (x, y), dot_radius) # draws grid of dots
            # pygame.draw.circle(screen, dot_colour, (x, y), dot_radius) # can replace the above with this line for the grid to change colour like the playing square
    
    r, g, b = update_color(r, g, b)

    """ Border on playing square """
    #pygame.draw.rect(screen, (100, 100, 100), player)
    #inner_rect = player.inflate(-4, -4)
    #pygame.draw.rect(screen, (r, g, b), inner_rect)

    pygame.draw.rect(screen, (r, g, b), player)
    draw_skull(skull_px, skull_py)

    draw_mastermind_panel(screen, guesses, feedback)

    # Check collision with skull
    if player.x == skull_px and player.y == skull_py:
        for i in range(4):  # two flashes
            pygame.draw.rect(screen, (0, 0, 0), player)
            pygame.display.update()
            pygame.time.delay(150)
            pygame.draw.rect(screen, (255, 255, 255), player)
            pygame.display.update()
            pygame.time.delay(150)
        game_over_text = title_font.render("Game Over", True, (255, 20, 147))
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 20))
        pygame.display.update()
        pygame.time.delay(2000)
        run = False

    if feedback: # checks feedback is non-empty
        if c == GOES*4 or feedback[-1] == ['correct','correct','correct','correct']:
            can_move = False
            if c == GOES*4:
                y1 = 70 + GOES * 45
                sequence_print = "".join(str(x) for x in sequence)
                game_over_surf = font.render(f"Game Lost: {sequence_print}", True, (0, 250, 180))
                screen.blit(game_over_surf, (SCREEN_WIDTH + 20, y1))
            if feedback[-1] == ['correct','correct','correct','correct']:
                y2 = 70 + len(feedback) * 45
                game_complete_surf = font.render("Game Complete", True, (0, 250, 180))
                screen.blit(game_complete_surf, (SCREEN_WIDTH + 20, y2))
    
    pygame.display.update()# most important line
    clock.tick(90) # frames per second

pygame.quit()
sys.exit()

########################################################################################################################################################################
