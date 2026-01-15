import pygame
from config import *
from entities import get_wrapped_draws

FONT = pygame.font.SysFont("comicsans", HUD_FONT_SIZE)


class GameWindow:
    def __init__(self):
        self.window_width = int(SCREEN_WIDTH * WINDOW_SCALE)
        self.window_height = int(SCREEN_HEIGHT * WINDOW_SCALE)
        flags = pygame.RESIZABLE if RESIZABLE else 0
        self.window = pygame.display.set_mode((self.window_width, self.window_height), flags)
        pygame.display.set_caption("Asteroids")
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

    def handle_resize(self, event):
        self.window_width = event.w
        self.window_height = event.h

    def render(self):
        scale = min(self.window_width / GAME_WIDTH, self.window_height / GAME_HEIGHT)
        scaled_w, scaled_h = int(GAME_WIDTH * scale), int(GAME_HEIGHT * scale)
        x_off = (self.window_width - scaled_w) // 2
        y_off = (self.window_height - scaled_h) // 2
        
        self.window.fill(BLACK)
        scaled = pygame.transform.smoothscale(self.game_surface, (scaled_w, scaled_h))
        self.window.blit(scaled, (x_off, y_off))
        pygame.display.update()


def draw_game(surface, asteroids, player, score, max_score):
    surface.fill(BLACK)
    
    for a in asteroids:
        for pos in get_wrapped_draws(a.pos, a.radius):
            surface.blit(a.surf, (pos[0] - a.radius, pos[1] - a.radius))
    
    for p in player.projectiles:
        for pos in get_wrapped_draws(p.pos, p.radius):
            surface.blit(p.surf, (pos[0] - p.radius, pos[1] - p.radius))
    
    if not (player.invulnerable and (player.invuln_timer // 8) % 2):
        surf = player.thrust_surf if player.thrusting else player.surf
        rotated = pygame.transform.rotate(surf, -player.angle)
        for pos in get_wrapped_draws(player.pos, player.size):
            rect = rotated.get_rect(center=(pos[0], pos[1]))
            surface.blit(rotated, rect)
    
    _draw_hud(surface, player, score, max_score)


def _draw_hud(surface, player, score, max_score):
    max_text = FONT.render(f"Max: {max_score}", True, WHITE)
    score_text = FONT.render(f"Score: {score}", True, WHITE)
    lives_text = FONT.render(f"Lives: {player.lives}", True, WHITE)
    
    if TRACK_MAX_SCORE:
        surface.blit(max_text, (GAME_WIDTH - max_text.get_width() - HUD_MARGIN, HUD_MARGIN))
        surface.blit(score_text, (GAME_WIDTH - score_text.get_width() - HUD_MARGIN,
                                HUD_MARGIN + max_text.get_height() + 5))
    else:
        surface.blit(score_text, (GAME_WIDTH - score_text.get_width() - HUD_MARGIN, HUD_MARGIN))
    surface.blit(lives_text, (HUD_MARGIN, HUD_MARGIN))
    
    icon_size = int(PLAYER_SIZE * 0.8)
    icon = pygame.transform.scale(player.surf, (icon_size, int(icon_size * 1.25)))
    for i in range(player.lives):
        surface.blit(icon, (HUD_MARGIN + i * (icon_size + 5), HUD_MARGIN + lives_text.get_height() + 5))
