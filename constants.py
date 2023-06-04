# Set up constants
# reading settings file

import configparser

config = configparser.ConfigParser()

# Read the INI file
config.read('settings.ini')

# Access values from sections
width = int(config['graphics']['WidthWindowSize'])
height = int(config['graphics']['HeightWindowSize'])


GAME_NAME = "RTS Game"
WINDOW_SIZE = (width, height) # using the config file to get our window size
GRID_SIZE = (80, 60)
CELL_SIZE = (WINDOW_SIZE[0] // GRID_SIZE[0], WINDOW_SIZE[1] // GRID_SIZE[1])
UNIT_SIZE = (WINDOW_SIZE[0] // 28, WINDOW_SIZE[0] // 28) # in theory WINDOW_SIZE[1] // 21, but let's stay consistent
BACKGROUND_COLOR = (30, 30, 30)
# GRID_COLOR = (50, 50, 50, 50)
UNIT_SELECTED_COLOR = (120, 160, 80)
UNIT_UNSELECTED_COLOR = (180, 255, 100)
SELECTION_COLOR = (255, 255, 255)
TARGET_CURSOR_MOVE_COLOR = (50, 150, 100)
TRANSPARENT = (0, 0, 0, 0)
