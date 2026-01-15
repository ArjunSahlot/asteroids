import pygame
import ctypes
import sys

if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

pygame.init()

# Game world
GAME_WIDTH = 1300
GAME_HEIGHT = 950

# Window
WINDOW_SCALE = 0.8
RESIZABLE = True
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# Timing
FPS = 90

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Player
PLAYER_SIZE = 40
PLAYER_MAX_SPEED = 10
PLAYER_ACCEL = 0.1
PLAYER_DRAG = 0.025
PLAYER_TURN_SPEED = 4
PLAYER_LIVES = 3
PLAYER_INVULN_FRAMES = 150

# Projectile
PROJ_SPEED = 8
PROJ_RADIUS = 3
PROJ_LIFETIME = 90
PROJ_MAX = 10
PROJ_COOLDOWN = 20

# Asteroid
ASTEROID_BASE_RADIUS = 50
ASTEROID_SIZES = {1: 2.0, 2: 1.2, 3: 0.5}
ASTEROID_SPEEDS = {1: 2, 2: 3, 3: 4}
ASTEROID_POINTS = {1: 20, 2: 50, 3: 100}

# HUD
HUD_FONT_SIZE = 40
HUD_MARGIN = 10

TRACK_MAX_SCORE = False