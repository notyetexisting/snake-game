import os
import pygame
from enum import Enum

# Screen settings
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GREEN = (0, 100, 0)

# Game settings
INITIAL_LENGTH = 3
SPEED_INCREASE = 0.5
MAX_SPEED = 20

# Paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3

# Load theme
def load_theme(theme_name='default'):
    themes = {
        'default': {
            'bg': (40, 40, 40),
            'grid': (30, 30, 30),
            'snake': (0, 255, 0),
            'food': (255, 0, 0),
            'text': (255, 255, 255),
            'obstacle': (100, 100, 100)
        },
        'dark': {
            'bg': (20, 20, 20),
            'grid': (10, 10, 10),
            'snake': (0, 200, 0),
            'food': (200, 50, 50),
            'text': (200, 200, 200),
            'obstacle': (80, 80, 80)
        },
        'retro': {
            'bg': (0, 0, 0),
            'grid': (20, 20, 20),
            'snake': (57, 255, 20),
            'food': (255, 0, 0),
            'text': (57, 255, 20),
            'obstacle': (100, 0, 0)
        }
    }
    return themes.get(theme_name.lower(), themes['default'])

# Initialize pygame
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.display.set_caption('Snake Game')

# Display settings
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
clock = pygame.time.Clock()

# Set allowed events for better performance
event_types = [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.VIDEORESIZE]
pygame.event.set_allowed(event_types)
