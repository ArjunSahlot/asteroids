import random
import pygame
import numpy as np
from config import *

def angle_to_vec(angle):
    rad = np.radians(angle)
    return np.array([np.sin(rad), -np.cos(rad)])

def wrap(pos):
    return pos % np.array([GAME_WIDTH, GAME_HEIGHT])

def get_wrapped_draws(pos, margin):
    result = [pos.copy()]
    x, y = pos
    if x < margin:
        result.append(pos + [GAME_WIDTH, 0])
    elif x > GAME_WIDTH - margin:
        result.append(pos - [GAME_WIDTH, 0])
    if y < margin:
        result.append(pos + [0, GAME_HEIGHT])
    elif y > GAME_HEIGHT - margin:
        result.append(pos - [0, GAME_HEIGHT])
    return result


class Player:
    def __init__(self, x=None, y=None, lives=PLAYER_LIVES):
        self.pos = np.array([x or GAME_WIDTH / 2, y or GAME_HEIGHT / 2], dtype=float)
        self.vel = np.zeros(2)
        self.angle = 0.0
        self.lives = lives
        self.size = PLAYER_SIZE
        
        self.invulnerable = True
        self.invuln_timer = 0
        self.shoot_timer = 0
        self.projectiles = []
        self.thrusting = False
        self._create_surfaces()
    
    def _create_surfaces(self):
        w, h = self.size, int(self.size * 1.25)
        self.surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self.thrust_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Draw ship as two lines meeting at top, plus cross bar
        pygame.draw.line(self.surf, WHITE, (0, h), (w // 2, 0), 3)
        pygame.draw.line(self.surf, WHITE, (w // 2, 0), (w, h), 3)
        pygame.draw.line(self.surf, WHITE, (int(w * 0.15), int(h * 0.7)), (int(w * 0.85), int(h * 0.7)), 3)
        
        self.thrust_surf.blit(self.surf, (0, 0))
        pygame.draw.polygon(self.thrust_surf, WHITE, [
            (int(w * 0.32), int(h * 0.7)),
            (w // 2, int(h * 1)),
            (int(w * 0.68), int(h * 0.7))
        ], 2)
    
    def update(self, events, dt=1.0):
        self.invuln_timer += 1
        if self.invulnerable and self.invuln_timer >= PLAYER_INVULN_FRAMES:
            self.invulnerable = False
        
        self.shoot_timer = max(0, self.shoot_timer - 1)
        self._handle_input(events, dt)
        self._apply_physics(dt)
        for p in self.projectiles:
            p.update(dt)
        self.projectiles = [p for p in self.projectiles if p.alive]
    
    def _handle_input(self, events, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle -= PLAYER_TURN_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.angle += PLAYER_TURN_SPEED * dt
        self.thrusting = keys[pygame.K_UP]
        
        shoot = keys[pygame.K_SPACE] or any(
            e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE for e in events
        )
        if shoot and self.shoot_timer == 0 and len(self.projectiles) < PROJ_MAX:
            direction = angle_to_vec(self.angle)
            spawn = self.pos + direction * (self.size * 0.6)
            self.projectiles.append(Projectile(spawn, self.angle))
            self.shoot_timer = PROJ_COOLDOWN
    
    def _apply_physics(self, dt):
        if self.thrusting:
            self.vel += angle_to_vec(self.angle) * PLAYER_ACCEL * dt
        
        speed = np.linalg.norm(self.vel)
        if speed > PLAYER_MAX_SPEED:
            self.vel = self.vel / speed * PLAYER_MAX_SPEED
            speed = PLAYER_MAX_SPEED
        
        if speed > 0:
            drag = min(PLAYER_DRAG * dt, speed)
            self.vel = self.vel * (1 - drag / speed)
        
        self.pos = wrap(self.pos + self.vel * dt)
    
    def hit(self):
        self.lives -= 1
        self.pos = np.array([GAME_WIDTH / 2, GAME_HEIGHT / 2])
        self.vel = np.zeros(2)
        self.angle = 0
        self.make_invulnerable()
    
    def make_invulnerable(self):
        self.invulnerable = True
        self.invuln_timer = 0
    
    @property
    def radius(self):
        return self.size * 0.4


class Projectile:
    def __init__(self, pos, angle):
        self.pos = pos.astype(float)
        self.vel = angle_to_vec(angle) * PROJ_SPEED
        self.radius = PROJ_RADIUS
        self.lifetime = PROJ_LIFETIME
        self.alive = True
        
        size = PROJ_RADIUS * 2
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, WHITE, (PROJ_RADIUS, PROJ_RADIUS), PROJ_RADIUS)
    
    def update(self, dt=1.0):
        self.pos = wrap(self.pos + self.vel * dt)
        self.lifetime -= 1
        self.alive = self.lifetime > 0


class Asteroid:
    def __init__(self, x, y, tier=1):
        self.pos = np.array([x, y], dtype=float)
        self.tier = tier
        self.angle = random.uniform(0, 360)
        
        scale = ASTEROID_SIZES[tier]
        self.radius = ASTEROID_BASE_RADIUS * scale
        self.speed = ASTEROID_SPEEDS[tier] * random.normalvariate(1.0, 0.2)
        self.vel = angle_to_vec(self.angle) * self.speed
        
        self._create_surface()
    
    def _create_surface(self):
        size = int(self.radius * 2)
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        ranges = np.array([
            [0, 0, 20, 20], [25, 5, 20, 20], [50, 2, 22, 22], [75, 20, 25, 25],
            [63, 37, 15, 15], [63, 60, 23, 28], [50, 80, 10, 15], [0, 70, 20, 23], [4, 34, 25, 21]
        ]) * size / 100
        
        points = [(random.randint(int(x), int(x + w)), random.randint(int(y), int(y + h)))
                  for x, y, w, h in ranges]
        pygame.draw.polygon(self.surf, WHITE, points, 3)
    
    def update(self, dt=1.0):
        self.pos = wrap(self.pos + self.vel * dt)
    
    def split(self):
        if self.tier >= 3:
            return []
        new_tier = self.tier + 1
        return [Asteroid(self.pos[0], self.pos[1], new_tier) for _ in range(2)]


def check_collision(pos1, r1, pos2, r2):
    diff = pos1 - pos2
    # Handle wrap-around
    if diff[0] > GAME_WIDTH / 2:
        diff[0] -= GAME_WIDTH
    elif diff[0] < -GAME_WIDTH / 2:
        diff[0] += GAME_WIDTH
    if diff[1] > GAME_HEIGHT / 2:
        diff[1] -= GAME_HEIGHT
    elif diff[1] < -GAME_HEIGHT / 2:
        diff[1] += GAME_HEIGHT
    return np.dot(diff, diff) < (r1 + r2) ** 2
