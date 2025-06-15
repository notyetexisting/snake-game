import os
import pygame
import random
import math
from enum import Enum
from config import *

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, images, x, y, frame_delay=5):
        super().__init__()
        self.images = images
        self.frame_index = 0
        self.frame_delay = frame_delay
        self.frame_counter = 0
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.animation_speed = 1.0

    def update(self):
        self.frame_counter += self.animation_speed
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.images)
            self.image = self.images[self.frame_index]

class SnakeHead(AnimatedSprite):
    def __init__(self, x, y):
        # Load snake head images for different directions
        head_images = [
            pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA),
            pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        ]
        # Simple colored heads for now - replace with actual sprites
        pygame.draw.circle(head_images[0], GREEN, (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//2)
        pygame.draw.circle(head_images[1], (200, 255, 200), (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//2)
        
        super().__init__(head_images, x * GRID_SIZE, y * GRID_SIZE, frame_delay=10)
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.last_position = (x, y)
        self.growing = False

    def update_direction(self, new_direction):
        # Prevent 180-degree turns
        if (new_direction == Direction.UP and self.direction != Direction.DOWN) or \
           (new_direction == Direction.DOWN and self.direction != Direction.UP) or \
           (new_direction == Direction.LEFT and self.direction != Direction.RIGHT) or \
           (new_direction == Direction.RIGHT and self.direction != Direction.LEFT):
            self.next_direction = new_direction

    def update(self):
        super().update()
        self.last_position = (self.rect.x // GRID_SIZE, self.rect.y // GRID_SIZE)
        self.direction = self.next_direction
        
        # Move the head
        dx, dy = self.direction.value
        self.rect.x = (self.rect.x + dx * GRID_SIZE) % WIDTH
        self.rect.y = (self.rect.y + dy * GRID_SIZE) % HEIGHT

class SnakeBody(AnimatedSprite):
    def __init__(self, x, y):
        # Load snake body images
        body_images = [
            pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA),
            pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        ]
        # Simple colored bodies for now - replace with actual sprites
        pygame.draw.rect(body_images[0], (0, 200, 0), (0, 0, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(body_images[1], (0, 150, 0), (0, 0, GRID_SIZE, GRID_SIZE))
        
        super().__init__(body_images, x * GRID_SIZE, y * GRID_SIZE, frame_delay=15)
        self.last_position = (x, y)

    def update_position(self, new_x, new_y):
        self.last_position = (self.rect.x // GRID_SIZE, self.rect.y // GRID_SIZE)
        self.rect.x = new_x * GRID_SIZE
        self.rect.y = new_y * GRID_SIZE

class Food(AnimatedSprite):
    def __init__(self, x, y):
        # Load food images for animation
        food_images = [
            pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA),
            pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        ]
        # Simple colored food for now - replace with actual sprites
        pygame.draw.circle(food_images[0], RED, (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//2)
        pygame.draw.circle(food_images[1], (255, 100, 100), (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//2)
        
        super().__init__(food_images, x * GRID_SIZE, y * GRID_SIZE, frame_delay=20)
        self.value = 10
        self.spawn_time = pygame.time.get_ticks()
        self.lifespan = 15000  # 15 seconds

    def should_despawn(self):
        return pygame.time.get_ticks() - self.spawn_time > self.lifespan

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, velocity, lifetime, size=3):
        super().__init__()
        self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size, size), size)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = velocity
        self.lifetime = lifetime
        self.alpha = 255
        self.size = size

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - 10)
        
        if self.alpha > 0:
            self.image.set_alpha(self.alpha)
class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def create_particles(self, x, y, color, count=10, size=3, speed=2):
        """Create a burst of particles at the given position"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            velocity = [
                math.cos(angle) * speed * random.uniform(0.5, 1.5),
                math.sin(angle) * speed * random.uniform(0.5, 1.5)
            ]
            lifetime = random.randint(20, 40)
            self.particles.append({
                'x': x, 'y': y,
                'vx': velocity[0], 'vy': velocity[1],
                'life': lifetime,
                'color': color,
                'size': size
            })
    
    def update(self):
        """Update all particles"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            # Remove dead particles
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def draw(self, surface):
        """Draw all particles"""
        for p in self.particles:
            alpha = min(255, p['life'] * 10)  # Fade out effect
            color = (*p['color'][:3], alpha) if len(p['color']) > 3 else p['color']
            
            # Create a surface with per-pixel alpha
            s = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (p['size'], p['size']), p['size'])
            surface.blit(s, (int(p['x'] - p['size']), int(p['y'] - p['size'])))
    
    def clear(self):
        """Remove all particles"""
        self.particles.clear()
