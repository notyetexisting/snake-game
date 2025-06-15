import pygame
import random
import time
import math
import os
import json
import sys
from enum import Enum
import threading
from config import *
from sprites import *

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption('Snake Game - Enhanced')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.score = 0
        self.high_score = self.load_high_score()
        self.theme = load_theme('default')
        self.font = pygame.font.Font(None, 36)
        self.particle_system = ParticleSystem()
        self.snake = []
        self.food = []
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.game_speed = FPS
        self.last_update = 0
        self.paused = False
        self.game_over = False
        self.init_assets()
        self.init_snake()
        self.spawn_food()

    def init_assets(self):
        # Load sounds
        self.sounds = {
            'eat': self.load_sound('eat.wav'),
            'game_over': self.load_sound('game_over.wav'),
            'powerup': self.load_sound('powerup.wav')
        }
        
        # Load images with error handling
        try:
            self.background = self.load_image('background.png')
            if self.background:
                self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        except:
            self.background = None

    def load_image(self, filename):
        try:
            path = os.path.join(IMAGES_DIR, filename)
            if os.path.exists(path):
                return pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
        return None

    def load_sound(self, filename):
        try:
            path = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(path):
                return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Error loading sound {filename}: {e}")
        return None

    def init_snake(self):
        self.snake = []
        start_x, start_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.snake_head = SnakeHead(start_x, start_y)
        self.snake_sprites = pygame.sprite.Group()
        self.snake_sprites.add(self.snake_head)
        
        # Add initial body segments
        for i in range(1, 4):
            self.add_segment(start_x - i, start_y)

    def add_segment(self, x, y):
        segment = SnakeBody(x, y)
        self.snake_sprites.add(segment)
        return segment

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            pos = (x * GRID_SIZE, y * GRID_SIZE)
            
            # Check if position is occupied by snake
            if not any(segment.rect.topleft == pos for segment in self.snake_sprites):
                self.food = Food(x, y)
                self.food_sprites = pygame.sprite.Group(self.food)
                return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                
                if not self.paused and not self.game_over:
                    if event.key == pygame.K_UP:
                        self.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN:
                        self.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT:
                        self.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT:
                        self.next_direction = Direction.RIGHT
                
                elif event.key == pygame.K_r:  # Reset game
                    self.reset_game()

    def update(self):
        if self.paused or self.game_over:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_update < 1000 // self.game_speed:
            return
        
        self.last_update = current_time

        # Update snake direction
        self.snake_head.update_direction(self.next_direction)
        
        # Store current positions before moving
        old_positions = [(segment.rect.x // GRID_SIZE, segment.rect.y // GRID_SIZE) 
                        for segment in self.snake_sprites]
        
        # Move head
        self.snake_head.update()
        
        # Update body segments to follow the segment in front of them
        for i in range(1, len(self.snake_sprites)):
            prev_x, prev_y = old_positions[i-1]
            self.snake_sprites.sprites()[i].update_position(prev_x, prev_y)
        
        # Check for collisions
        self.check_collisions()

    def check_collisions(self):
        # Check food collision
        head_rect = self.snake_head.rect
        if pygame.sprite.spritecollide(self.snake_head, self.food_sprites, True):
            self.score += 10
            self.sounds['eat'].play()
            self.spawn_food()
            # Add new segment at the end
            last_segment = self.snake_sprites.sprites()[-1]
            self.add_segment(*divmod(last_segment.rect.x, GRID_SIZE), 
                           *divmod(last_segment.rect.y, GRID_SIZE))
            
            # Create particle effect
            self.particle_system.create_particles(
                head_rect.centerx, head_rect.centery, 
                (255, 255, 0), count=20, size=4, speed=3
            )
        
        # Check self collision (skip head)
        if pygame.sprite.spritecollide(self.snake_head, 
                                     [s for s in self.snake_sprites if s != self.snake_head], 
                                     False):
            self.game_over = True
            self.sounds['game_over'].play()

    def draw(self):
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.theme['bg'])
        
        # Draw grid (semi-transparent)
        self.draw_grid()
        
        # Draw food and snake
        self.food_sprites.draw(self.screen)
        self.snake_sprites.draw(self.screen)
        
        # Draw particles
        self.particle_system.update()
        self.particle_system.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        if self.paused:
            self.draw_pause_screen()
        elif self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40, 50), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40, 50), (0, y), (WIDTH, y))

    def draw_hud(self):
        # Score
        score_surf = self.font.render(f'Score: {self.score}', True, self.theme['text'])
        self.screen.blit(score_surf, (10, 10))
        
        # High score
        high_score_surf = self.font.render(f'High Score: {self.high_score}', True, self.theme['text'])
        self.screen.blit(high_score_surf, (10, 50))
        
        # FPS counter (for debugging)
        fps_surf = self.font.render(f'FPS: {int(self.clock.get_fps())}', True, self.theme['text'])
        self.screen.blit(fps_surf, (WIDTH - 120, 10))

    def draw_pause_screen(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        self.screen.blit(s, (0, 0))
        
        text = self.font.render('PAUSED', True, WHITE)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(text, text_rect)
        
        subtext = self.font.render('Press ESC to resume', True, WHITE)
        subtext_rect = subtext.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        self.screen.blit(subtext, subtext_rect)

    def draw_game_over(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (0, 0))
        
        text = self.font.render('GAME OVER', True, RED)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(text, text_rect)
        
        score_text = self.font.render(f'Final Score: {self.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        self.screen.blit(score_text, score_rect)
        
        subtext = self.font.render('Press R to restart', True, WHITE)
        subtext_rect = subtext.get_rect(center=(WIDTH//2, HEIGHT//2 + 70))
        self.screen.blit(subtext, subtext_rect)

    def reset_game(self):
        self.score = 0
        self.game_over = False
        self.paused = False
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.game_speed = FPS
        self.snake_sprites.empty()
        self.init_snake()
        self.spawn_food()
        self.particle_system = ParticleSystem()

    def load_high_score(self):
        try:
            with open('highscore.dat', 'rb') as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        if self.score > self.high_score:
            with open('highscore.dat', 'wb') as f:
                f.write(str(self.score).encode())

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # Cap at 60 FPS
        
        self.save_high_score()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
