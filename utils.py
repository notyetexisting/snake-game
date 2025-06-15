def load_image(file_path):
    """Load an image from the specified file path."""
    try:
        image = t.PhotoImage(file=file_path)
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def load_sound(file_path):
    """Load a sound from the specified file path."""
    try:
        sound = pygame.mixer.Sound(file_path)
        return sound
    except Exception as e:
        print(f"Error loading sound: {e}")
        return None

def check_collision(obj1, obj2):
    """Check for collision between two objects."""
    return obj1.distance(obj2) < 20

def update_score(current_score, high_score):
    """Update the score and return the new high score if necessary."""
    if current_score > high_score:
        high_score = current_score
    return high_score

def reset_game(segments, score_display, high_score):
    """Reset the game state after a game over."""
    for segment in segments:
        segment.goto(1000, 1000)
    segments.clear()
    return 0, high_score  # Reset score and return high score