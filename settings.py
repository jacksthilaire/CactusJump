# HOLDING VARIABLES, SETTINGS, COLORS, ETC

# width and height of window, fps of game
width = 500
height = 600
fps = 30

# text variables
title = "Cactus Jump"
FONT_NAME = 'impact'
HSFILE = "hscore.txt"
SPRITESHEET = "spritesheet_jumper.png"
CHAR_SPRITE = "cactussprite.png"

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (189, 42, 34)
GREEN = (84, 163, 80)
BLUE = (140, 195, 250)
GREY = (94, 87, 86)

# player properties
PLAYER_ACC = 0.9
PLAYER_FRICTION = -0.10
PLAYER_GRAVITY = 1.0

# starting platforms
PLATFORM_LIST = [((width / 2) - 10, (height / 2) + 20), # main platform at bottom
                 (50, height - 180),
                 (200, height - 390),
                 (70, height - 480)]

# pow settings
COIN_VAL = 3
POW_RATE = 15

PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
ENEMY_LAYER = 2