import pygame
import pygame_menu
from constants import *
import configparser

# Set up Pygame
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(GAME_NAME)
clock = pygame.time.Clock()
FPS = 60

def set_difficulty(value, difficulty):
    # Do the job here !
    pass

def set_graphics(value, new_window_size):
    config = configparser.ConfigParser()
    config.read('settings.ini', encoding='utf-8')

    config['graphics']['WidthWindowSize'] = str(new_window_size[0])
    config['graphics']['HeightWindowSize'] = str(new_window_size[1])

    # Write the INI file
    with open('settings.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    pass

def start_the_game():
    pause_menu.enable()
    # Do the job here !

def resume():
    pause_menu.disable()

def disabled():
    pause_menu.disable()

pause_menu = pygame_menu.Menu('Menu', SCREEN_SIZE[0], SCREEN_SIZE[1], theme=pygame_menu.themes.THEME_DARK)

options_menu = pygame_menu.Menu('Options', SCREEN_SIZE[0], SCREEN_SIZE[1], theme=pygame_menu.themes.THEME_DARK)

graphical_options_menu = pygame_menu.Menu('Options', SCREEN_SIZE[0], SCREEN_SIZE[1], theme=pygame_menu.themes.THEME_DARK)

# menu.add.text_input('Name :', default='John Doe')
# menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
pause_menu.add.button('Play', resume)
pause_menu.add.button('Options', options_menu)
pause_menu.add.button('Quit', pygame_menu.events.EXIT)

options_menu.add.button('Graphics', graphical_options_menu)
options_menu.add.button('Return', pygame_menu.events.BACK)

graphical_options_menu.add.selector('Resolution', [('1920x1080', (1920,1080)), ('1280x720', (1280, 720)), ('800x600', (800, 600))], onchange=set_graphics)
graphical_options_menu.add.button('Return', pygame_menu.events.BACK)
