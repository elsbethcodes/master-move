""" Libraries """ 
import pygame
import sys
import math
import random

pygame.init()

""" Global variables """
TILE_SIZE = 50
SCREEN_WIDTH = TILE_SIZE*15
SCREEN_HEIGHT = TILE_SIZE*13
PANEL_WIDTH = TILE_SIZE*5
GOES = 12

screen = pygame.display.set_mode((SCREEN_WIDTH + PANEL_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

CENTRE_SCREEN = [SCREEN_WIDTH/2 - TILE_SIZE/2, SCREEN_HEIGHT/2 - TILE_SIZE/2]
player = pygame.Rect((CENTRE_SCREEN[0], CENTRE_SCREEN[1], TILE_SIZE, TILE_SIZE))
r, g, b = 0, 0, 255
colour_direction = 1
dot_colour = (0, 255, 128)
dot_radius = 2

font = pygame.font.SysFont("Courier", 20, bold=True)
title_font = pygame.font.SysFont("Courier", 28, bold=True)

""" Global lists """
guesses = []
feedback = []
sequence = [random.choice(['↑', '↓', '→', '←']) for x in range(4)]

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
skull_tile = [0, 0]

game_state = "instructions"  # "instructions" or "playing"

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

def draw_mastermind_panel(screen, guesses, feedback):
    panel_x = SCREEN_WIDTH
    screen.fill((20, 20, 20), (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))
    title_surf = title_font.render("Mastermove", True, (0, 250, 180))
    screen.blit(title_surf, (panel_x + 20, 20))

    for i, guess in enumerate(guesses):
        y = 70 + i * 45
        guess_str = " ".join(guess)
        guess_surf = font.render(f"{i+1}  {guess_str}", True, (0, 250, 180))
        screen.blit(guess_surf, (panel_x + 20, y))

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

def add_item(item, lst):
    if not lst or len(lst[-1]) == 4:
        lst.append([item])
    else:
        lst[-1].append(item)

def get_feedback(guess, solution):
    feedback = []
    temp_solution = solution.copy()
    temp_guess = guess.copy()
    for i in range(4):
        if temp_guess[i] == temp_solution[i]:
            feedback.append('correct')
            temp_solution[i] = None
            temp_guess[i] = None
    for i in range(4):
        if temp_guess[i] is not None and temp_guess[i] in temp_solution:
            feedback.append('incorrect position')
            temp_solution[temp_solution.index(temp_guess[i])] = None
        elif temp_guess[i] is not None:
            feedback.append('miss')
    return feedback

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

def draw_instruction_screen():
    screen.fill((0, 0, 0))
    lines = [
        "Mastermove rules",
        "",
        "Guess the sequence of arrows by moving the square.",
        "Use the feedback to improve your guesses.",
        "Avoid the skull chaser.",
        "",
        "Pegs explained",
        "Green peg: correct arrow correct position",
        "Pink peg: correct arrow wrong position",
        "Black peg: wrong arrow",
        "",
        "The position of the pegs does not",
        "correspond to the arrow positions.",
        "",
        "Click START to begin."
    ]
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, (0, 250, 180))
        screen.blit(text_surf, (50, 30 + i * 30))

    button_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT - 100, 120, 40)
    pygame.draw.rect(screen, (0, 250, 180), button_rect)
    start_text = font.render("START", True, (0, 0, 0))
    screen.blit(start_text, (button_rect.x + 25, button_rect.y + 8))
    return button_rect

run = True
can_move = True
c = 0

while run:
    if game_state == "instructions":
        start_button = draw_instruction_screen()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_state = "playing"

    elif game_state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and can_move:
                key = pygame.key.get_pressed()
                if key[pygame.K_LEFT]:
                    player.move_ip(-TILE_SIZE,0)
                    can_move = False
                    add_item('←', guesses)
                    if len(guesses[-1]) == 4:
                        feedback.append(sorted(get_feedback(guesses[-1], sequence)))
                    c+=1
                elif key[pygame.K_RIGHT]:
                    player.move_ip(TILE_SIZE,0)
                    can_move = False
                    add_item('→', guesses)
                    if len(guesses[-1]) == 4:
                        feedback.append(sorted(get_feedback(guesses[-1], sequence)))
                    c+=1
                elif key[pygame.K_UP]:
                    player.move_ip(0,-TILE_SIZE)
                    can_move = False
                    add_item('↑', guesses)
                    if len(guesses[-1]) == 4:
                        feedback.append(sorted(get_feedback(guesses[-1], sequence)))
                    c+=1
                elif key[pygame.K_DOWN]:
                    player.move_ip(0,TILE_SIZE)
                    can_move = False
                    add_item('↓', guesses)
                    if len(guesses[-1]) == 4:
                        feedback.append(sorted(get_feedback(guesses[-1], sequence)))
                    c+=1

            if event.type == pygame.KEYUP:
                can_move = True

        if player.left < 0:
            player.right = SCREEN_WIDTH
        elif player.right > SCREEN_WIDTH:
            player.left = 0
        if player.top < 0:
            player.bottom = SCREEN_HEIGHT
        elif player.bottom > SCREEN_HEIGHT:
            player.top = 0

        skull_px = skull_tile[0] * TILE_SIZE
        skull_py = skull_tile[1] * TILE_SIZE

        current_time = pygame.time.get_ticks()
        if current_time - skull_timer >= SKULL_MOVE_INTERVAL and can_move:
            skull_timer = current_time
            dx = player.x - skull_tile[0] * TILE_SIZE
            dy = player.y - skull_tile[1] * TILE_SIZE
            if abs(dx) > abs(dy):
                skull_tile[0] += 1 if dx > 0 else -1
            elif dy != 0:
                skull_tile[1] += 1 if dy > 0 else -1

        screen.fill((0,0,0))

        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
                pygame.draw.circle(screen, dot_colour, (x, y), dot_radius)

        r, g, b = update_color(r, g, b)
        pygame.draw.rect(screen, (r, g, b), player)
        draw_skull(skull_px, skull_py)
        draw_mastermind_panel(screen, guesses, feedback)

        if player.x == skull_px and player.y == skull_py:
            for i in range(4):
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

        if feedback:
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

        pygame.display.update()
        clock.tick(90)

pygame.quit()
sys.exit()
