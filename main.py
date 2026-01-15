import pygame
import random
from config import GAME_WIDTH, GAME_HEIGHT, FPS, ASTEROID_POINTS, TRACK_MAX_SCORE
from entities import Player, Asteroid, check_collision
from renderer import GameWindow, draw_game


def create_asteroids(count):
    asteroids = []
    for _ in range(count):
        x = random.randint(100, GAME_WIDTH - 100)
        y = random.randint(100, GAME_HEIGHT - 100)
        asteroids.append(Asteroid(x, y, tier=1))
    return asteroids


def check_collisions(player, asteroids):
    score = 0
    new_asteroids = asteroids[:]
    
    for asteroid in asteroids:
        if not player.invulnerable:
            if check_collision(player.pos, player.radius, asteroid.pos, asteroid.radius):
                player.hit()
                new_asteroids.remove(asteroid)
                new_asteroids.extend(asteroid.split())
                continue
        
        for proj in player.projectiles[:]:
            if check_collision(proj.pos, proj.radius, asteroid.pos, asteroid.radius):
                score += ASTEROID_POINTS[asteroid.tier]
                proj.alive = False
                if asteroid in new_asteroids:
                    new_asteroids.remove(asteroid)
                    new_asteroids.extend(asteroid.split())
                break
    
    player.projectiles = [p for p in player.projectiles if p.alive]
    return new_asteroids, score


def load_max_score():
    try:
        with open("max_score.txt") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_max_score(score):
    with open("max_score.txt", "w") as f:
        f.write(str(score))


def main():
    game_window = GameWindow()
    player = Player()
    asteroids = []
    clock = pygame.time.Clock()
    score, wave = 0, 0
    max_score = load_max_score()

    while True:
        dt = clock.tick(FPS) / (1000.0 / FPS)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.VIDEORESIZE:
                game_window.handle_resize(event)
            if event.type == pygame.QUIT:
                if TRACK_MAX_SCORE:
                    save_max_score(max_score)
                return

        if not asteroids:
            score += wave * 20
            wave = min(wave + 1, 7)
            player.make_invulnerable()
            asteroids = create_asteroids(wave)

        player.update(events, dt)
        for asteroid in asteroids:
            asteroid.update(dt)
        
        asteroids, hit_score = check_collisions(player, asteroids)
        score += hit_score
        max_score = max(max_score, score)

        draw_game(game_window.game_surface, asteroids, player, score, max_score)
        game_window.render()

        if player.lives <= 0:
            pygame.time.delay(2000)
            if TRACK_MAX_SCORE:
                save_max_score(max_score)
            return


if __name__ == "__main__":
    main()
