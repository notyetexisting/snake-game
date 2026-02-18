import pygame

def load_image(file_path):
    """Load an image using pygame."""
    try:
        return pygame.image.load(file_path).convert_alpha()
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def load_sound(file_path):
    """Load a sound using pygame."""
    try:
        return pygame.mixer.Sound(file_path)
    except Exception as e:
        print(f"Error loading sound: {e}")
        return None

def check_collision(pos1, pos2, dist=20):
    """Check for collision between two positions."""
    return pygame.math.Vector2(pos1).distance_to(pos2) < dist

def update_score(current_score, high_score):
    """Update the score and return the new high score if necessary."""
    return max(current_score, high_score)
