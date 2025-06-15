import pygame
import random
import time
import math
import os
import json
import sys
import glob

# Fix: Import winsound only on Windows, else use a dummy function
if os.name == "nt":
    import winsound
    def beep(freq, dur):
        try:
            winsound.Beep(freq, dur)
        except RuntimeError:
            pass
else:
    def beep(freq, dur):
        pass

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 700, 700
SNAKE_SIZE = 32
APPLE_SIZE = 22
FPS = 10

# --- Themes ---
THEMES = {
    "Neon-Retro": {
        "bg": (10, 10, 30), "snake": (57, 255, 20), "food": (255, 0, 255), "text": (255, 255, 0),
        "font": None
    },
    "Dark Modern": {
        "bg": (30, 30, 30), "snake": (200, 200, 200), "food": (255, 80, 80), "text": (255, 255, 255),
        "font": "JetBrainsMono-BoldItalic.ttf"
    },
    "Solarized Light": {
        "bg": (253, 246, 227), "snake": (38, 139, 210), "food": (220, 50, 47), "text": (101, 123, 131),
        "font": "Inconsolata-Regular.ttf"
    },
    "Monokai": {
        "bg": (39, 40, 34), "snake": (249, 38, 114), "food": (166, 226, 46), "text": (248, 248, 242),
        "font": "FiraCode-Retina.ttf.otf"
    },
    "Kimbie Dark": {
        "bg": (36, 32, 28), "snake": (221, 136, 31), "food": (232, 74, 95), "text": (197, 200, 198),
        "font": "JetBrainsMono-ExtraBold.ttf"
    },
    "Abyss": {
        "bg": (20, 22, 34), "snake": (0, 122, 204), "food": (255, 85, 0), "text": (204, 204, 204),
        "font": "UbuntuMono-Regular.ttf"
    },
    "Red": {
        "bg": (40, 0, 0), "snake": (255, 40, 40), "food": (255, 200, 0), "text": (255, 255, 255),
        "font": "UbuntuMono-Bold.ttf"
    },
    "Solarized Dark": {
        "bg": (0, 43, 54), "snake": (38, 139, 210), "food": (220, 50, 47), "text": (133, 153, 0),
        "font": "Inconsolata-Bold.ttf"
    },
    "Monokai Dimmed": {
        "bg": (24, 25, 21), "snake": (249, 38, 114), "food": (166, 226, 46), "text": (197, 200, 198),
        "font": "UbuntuMono-Italic.ttf"
    },
    "Demon Dark": {
        "bg": (0, 0, 0), "snake": (255, 0, 0), "food": (180, 0, 0), "text": (255, 0, 0),
        "font": "UbuntuMono-BoldItalic.ttf"
    },
}

theme_name = "Neon-Retro"
theme = THEMES[theme_name]

def get_theme_font(theme_name, size=36):
    font_file = THEMES[theme_name].get("font")
    if font_file:
        font_path = os.path.join(
            r"C:\Users\notye\OneDrive\Documents\Python Projects by me\snake-game\src\Fonts", font_file
        )
        try:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
            else:
                print(f"Warning: Font file '{font_file}' not found. Using default font.")
                return pygame.font.SysFont(None, size)
        except Exception:
            return pygame.font.SysFont(None, size)
    else:
        return pygame.font.SysFont(None, size)

font = get_theme_font(theme_name, 36)
sound_on = True

# --- Setup ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE(X) by Ahmed Sajid")
clock = pygame.time.Clock()
def load_and_scale(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        # Maintain aspect ratio and center the image in a square surface
        img_rect = img.get_rect()
        scale_factor = min(size / img_rect.width, size / img_rect.height)
        new_width = int(img_rect.width * scale_factor)
        new_height = int(img_rect.height * scale_factor)
        img = pygame.transform.smoothscale(img, (new_width, new_height))
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.blit(img, ((size - new_width) // 2, (size - new_height) // 2))
        return surface
    except pygame.error as e:
        print(f"Error loading image at '{path}': {e}")
        return pygame.Surface((size, size), pygame.SRCALPHA)  # Transparent fallback

snake_head_img = load_and_scale(
    r"C:\Users\notye\OneDrive\Documents\Python Projects by me\snake-game\src\assets\images\snake_head.png", SNAKE_SIZE
)
snake_body_img = load_and_scale(
    r"C:\Users\notye\OneDrive\Documents\Python Projects by me\snake-game\src\assets\images\snake_body.png", SNAKE_SIZE
)
apple_img = load_and_scale(
    r"C:\Users\notye\OneDrive\Documents\Python Projects by me\snake-game\src\assets\images\food.png", APPLE_SIZE
)
bomb_img = load_and_scale(
    r"C:\Users\notye\OneDrive\Documents\Python Projects by me\snake-game\src\assets\images\Bomb.png", SNAKE_SIZE + 10
)

# --- Leaderboard Management ---
LEADERBOARD_FILE = "survival_leaderboard.json"
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as f:
        return json.load(f)
def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)
def update_leaderboard(name, score, time_sec):
    leaderboard = load_leaderboard()
    leaderboard.append({"name": name, "score": score, "time": time_sec})
    leaderboard = sorted(leaderboard, key=lambda x: (-x["score"], x["time"]))[:10]
    save_leaderboard(leaderboard)

# --- Particle Effect ---
particles = []
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(10, 20)
        self.color = color
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 4)
def particle_crash_effect(snake):
    global particles
    for segment in snake:
        for _ in range(12):
            particles.append(Particle(segment[0] + SNAKE_SIZE // 2, segment[1] + SNAKE_SIZE // 2, theme["snake"]))
    for _ in range(20):
        screen.fill(theme["bg"])
        for p in particles:
            p.update()
            p.draw(screen)
        pygame.display.flip()
        beep(1000, 100)
    particles.clear()

def play_sound(sound_type=None):
    if not sound_on:
        return
    if sound_type == "eat":
        beep(1000, 100)
    elif sound_type == "gameover":
        beep(300, 300)

def draw_button(rect, text, active=False):
    if active:
        pygame.draw.rect(screen, (80, 80, 180), rect.inflate(8, 8), border_radius=8)
    pygame.draw.rect(screen, (200, 200, 200) if active else (150, 150, 150), rect, border_radius=8)
    label = font.render(text, True, theme["text"])
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

def draw_timer(start_ticks):
    elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
    mins = elapsed // 60
    secs = elapsed % 60
    timer_label = font.render(f"Time: {mins:02}:{secs:02}", True, theme["text"])
    screen.blit(timer_label, (WIDTH - timer_label.get_width() - 20, 10))

def get_new_food_position(snake):
    min_x = 0
    max_x = WIDTH - SNAKE_SIZE
    min_y = 0
    max_y = HEIGHT - SNAKE_SIZE
    while True:
        pos = (
            random.randrange(min_x, max_x + 1, SNAKE_SIZE),
            random.randrange(min_y, max_y + 1, SNAKE_SIZE)
        )
        if pos not in snake:
            return pos

def is_on_apple(snake_head, food_position):
    offset = (SNAKE_SIZE - APPLE_SIZE) // 2
    apple_center = (food_position[0] + offset + APPLE_SIZE // 2, food_position[1] + offset + APPLE_SIZE // 2)
    snake_center = (snake_head[0] + SNAKE_SIZE // 2, snake_head[1] + SNAKE_SIZE // 2)
    return (abs(snake_center[0] - apple_center[0]) < SNAKE_SIZE // 2) and (abs(snake_center[1] - apple_center[1]) < SNAKE_SIZE // 2)

def is_on_bomb(snake_head, bomb_position):
    offset = (SNAKE_SIZE + 10 - SNAKE_SIZE) // 2
    bomb_center = (bomb_position[0] + offset + (SNAKE_SIZE + 10) // 2, bomb_position[1] + offset + (SNAKE_SIZE + 10) // 2)
    snake_center = (snake_head[0] + SNAKE_SIZE // 2, snake_head[1] + SNAKE_SIZE // 2)
    return (abs(snake_center[0] - bomb_center[0]) < SNAKE_SIZE // 2) and (abs(snake_center[1] - bomb_center[1]) < SNAKE_SIZE // 2)

def set_theme(new_theme_name):
    global theme_name, theme, font
    theme_name = new_theme_name
    theme = THEMES[theme_name]
    font = get_theme_font(theme_name, 36)

# --- Main Game Functions (home_screen, settings_screen, etc.) ---
# All UI text below should use English strings directly, e.g. "Settings", "Resume", etc.

# --- Home Screen ---
def home_screen():
    buttons = [
        ("Resume", pygame.Rect(60, 120, 240, 50)),
        ("Play New Game", pygame.Rect(60, 190, 240, 50)),
        ("Challenges", pygame.Rect(60, 260, 240, 50)),
        ("Leaderboard", pygame.Rect(60, 330, 240, 50)),
        ("Settings", pygame.Rect(60, 400, 240, 50)),
        ("Help and Licensing", pygame.Rect(60, 470, 240, 50)),
        ("Send us Feedback", pygame.Rect(60, 540, 240, 50)),
        ("Quit", pygame.Rect(60, 610, 240, 50)),
    ]
    selected = 1
    while True:
        screen.fill(theme["bg"])
        # Move the title to the left
        title = font.render("SNAKE(X) BY AHMED SAJID", True, theme["text"])
        screen.blit(title, (30, 40))
        for i, (text, rect) in enumerate(buttons):
            draw_button(rect, text, active=(i == selected))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(buttons)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    return buttons[selected][0]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text, rect) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        return text

# --- Settings Screen ---
def settings_screen():
    global FPS, theme_name, theme, sound_on, font, WIDTH, HEIGHT, screen
    themes_list = list(THEMES.keys())
    theme_idx = themes_list.index(theme_name)
    sizes = [(500, 500), (600, 600), (700, 700), (800, 600), (900, 700), (1000, 800)]
    size_idx = [i for i, s in enumerate(sizes) if s == (WIDTH, HEIGHT)]
    size_idx = size_idx[0] if size_idx else 2  # Default to 700x700
    options = [
        "Speed (FPS):",
        "Theme:",
        "Sound:",
        "Screen Size:",
        "Back"
    ]
    selected = 0
    editing = False
    while True:
        screen.fill(theme["bg"])
        title = font.render("Settings", True, theme["text"])
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        for i, opt in enumerate(options):
            y = 160 + i*80
            if opt == "Speed (FPS):":
                val = f"{FPS}"
            elif opt == "Theme:":
                val = themes_list[theme_idx]
            elif opt == "Sound:":
                val = "On" if sound_on else "Off"
            elif opt == "Screen Size:":
                val = f"{sizes[size_idx][0]}x{sizes[size_idx][1]}"
            else:
                val = ""
            rect = pygame.Rect(WIDTH//2-150, y-10, 300, 60)
            if i == selected:
                pygame.draw.rect(screen, (80, 80, 180), rect, border_radius=12)
            label = font.render(f"{opt} {val}", True, (255,255,0) if i == selected else theme["text"])
            screen.blit(label, (WIDTH//2 - label.get_width()//2, y))
        if editing and options[selected] != "Back":
            hint = font.render("Use LEFT/RIGHT to change, ENTER to confirm, ESC to cancel", True, theme["text"])
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if not editing:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if options[selected] == "Back":
                            return
                        else:
                            editing = True
                    elif event.key == pygame.K_ESCAPE:
                        return
                else:
                    if event.key == pygame.K_LEFT:
                        if options[selected] == "Speed (FPS):":
                            FPS = max(5, FPS - 1)
                        elif options[selected] == "Theme:":
                            theme_idx = (theme_idx - 1) % len(themes_list)
                            set_theme(themes_list[theme_idx])
                        elif options[selected] == "Sound:":
                            sound_on = not sound_on
                        elif options[selected] == "Screen Size:":
                            size_idx = (size_idx - 1) % len(sizes)
                    elif event.key == pygame.K_RIGHT:
                        if options[selected] == "Speed (FPS):":
                            FPS = min(60, FPS + 1)
                        elif options[selected] == "Theme:":
                            theme_idx = (theme_idx + 1) % len(themes_list)
                            set_theme(themes_list[theme_idx])
                        elif options[selected] == "Sound:":
                            sound_on = not sound_on
                        elif options[selected] == "Screen Size:":
                            size_idx = (size_idx + 1) % len(sizes)
                    elif event.key == pygame.K_RETURN:
                        if options[selected] == "Screen Size:":
                            WIDTH, HEIGHT = sizes[size_idx]
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))
                            global game_bg
                            # game_bg = load_game_bg()  # Removed: load_game_bg is not defined
                        editing = False
                    elif event.key == pygame.K_ESCAPE:
                        editing = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return

# --- Feedback Screen ---
def feedback_screen():
    info = [
        "Send us Feedback! or Report a bug ",
        "",
        "Email: notyetexisting2@gmail.com",
        "GitHub: github.com/notyetexisting",
        "",
        "Press any key or click to return."
    ]
    while True:
        screen.fill(theme["bg"])
        y = 180
        for line in info:
            label = font.render(line, True, theme["text"])
            screen.blit(label, (WIDTH//2 - label.get_width()//2, y))
            y += 50
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return

# --- Help and Licensing Screen ---
def help_and_licensing_screen():
    instructions = [
        "Instructions:",
        "- Use the arrow keys to move the snake.",
        "- Eat the apple to grow and score points.",
        "- Avoid hitting yourself.",
        "- Press ESC to pause and return to the menu.",
        "",
        "Licensing:",
        "MIT License",
        "Copyright (c) 2025 Ahmed Sajid",
        "Permission is hereby granted, free of charge, to any person obtaining a copy",
        "of this software and associated documentation files (the \"Software\"), to deal",
        "in the Software without restriction, including without limitation the rights",
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell",
        "copies of the Software, and to permit persons to whom the Software is",
        "furnished to do so, subject to the following conditions:",
        "",
        "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND."
    ]
    scroll_offset = 0
    line_height = 30
    max_offset = max(0, len(instructions) * line_height - HEIGHT + 40)
    while True:
        screen.fill(theme["bg"])
        y = 40 - scroll_offset
        for line in instructions:
            label = font.render(line, True, theme["text"])
            screen.blit(label, (30, y))
            y += line_height
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    scroll_offset = min(scroll_offset + line_height, max_offset)
                elif event.key == pygame.K_UP:
                    scroll_offset = max(scroll_offset - line_height, 0)
                else:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return

# --- Leaderboard Screen ---
def leaderboard_screen():
    leaderboard = load_leaderboard()
    screen.fill(theme["bg"])
    title = font.render("Survival Leaderboard", True, theme["text"])
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
    y = 120
    header = font.render("Rank  Name         Score   Time(s)", True, theme["text"])
    screen.blit(header, (WIDTH//2 - header.get_width()//2, y))
    y += 40
    for idx, entry in enumerate(leaderboard):
        line = f"{idx+1:>2}. {entry['name'][:10]:<10}   {entry['score']:<5}   {entry['time']:<5}"
        label = font.render(line, True, theme["text"])
        screen.blit(label, (WIDTH//2 - label.get_width()//2, y))
        y += 35
    if not leaderboard:
        label = font.render("No records yet.", True, theme["text"])
        screen.blit(label, (WIDTH//2 - label.get_width()//2, y))
    prompt = font.render("Press any key or click to return.", True, theme["text"])
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 60))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False

# --- Challenges Screen ---
def challenges_screen():
    buttons = [
        ("Survival Mode", pygame.Rect(WIDTH//2-120, 220, 240, 60)),
        ("Back", pygame.Rect(WIDTH//2-120, 320, 240, 60)),
    ]
    selected = 0
    while True:
        screen.fill(theme["bg"])
        title = font.render("Challenges", True, theme["text"])
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        for i, (text, rect) in enumerate(buttons):
            draw_button(rect, text, active=(i == selected))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected = 1 - selected
                elif event.key == pygame.K_RETURN:
                    if buttons[selected][0] == "Survival Mode":
                        survival_mode()
                    elif buttons[selected][0] == "Back":
                        return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text, rect) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        if text == "Survival Mode":
                            survival_mode()
                        elif text == "Back":
                            return

# --- Pause Screen ---
def pause_screen():
    buttons = [
        ("Resume", pygame.Rect(WIDTH//2-100, 320, 200, 50)),
        ("Return to Menu", pygame.Rect(WIDTH//2-100, 390, 200, 50)),
    ]
    selected = 0
    while True:
        screen.fill(theme["bg"])
        title = font.render("Paused", True, (0, 0, 200))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        for i, (text, rect) in enumerate(buttons):
            draw_button(rect, text, active=(i == selected))
        info = font.render("Press 'R' to Resume", True, theme["text"])
        screen.blit(info, (WIDTH//2 - info.get_width()//2, 250))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected = 1 - selected
                elif event.key == pygame.K_RETURN:
                    return buttons[selected][0]
                elif event.key == pygame.K_r:
                    return "Resume"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text, rect) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        return text

# --- End Game Screen ---
def end_game_screen(score, high_score):
    buttons = [
        ("Play Again", pygame.Rect(WIDTH//2-100, 320, 200, 50)),
        ("Return to Menu", pygame.Rect(WIDTH//2-100, 390, 200, 50)),
    ]
    selected = 0
    while True:
        screen.fill(theme["bg"])
        title = font.render("SNAKE(X) - You Lost", True, (200, 0, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        score_label = font.render(f"Your Score: {score}", True, theme["text"])
        screen.blit(score_label, (WIDTH//2 - score_label.get_width()//2, 180))
        high_label = font.render(f"High Score: {high_score}", True, theme["text"])
        screen.blit(high_label, (WIDTH//2 - high_label.get_width()//2, 230))
        for i, (text, rect) in enumerate(buttons):
            draw_button(rect, text, active=(i == selected))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected = 1 - selected
                elif event.key == pygame.K_RETURN:
                    return buttons[selected][0]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (text, rect) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        return text

# --- Startup Screen ---
def startup_screen():
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))
    alpha = 255
    show = True
    while show:
        screen.fill(theme["bg"])
        title = font.render("SNAKE(X) BY AHMED SAJID", True, theme["text"])
        prompt = font.render("PRESS ENTER", True, theme["text"])
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    for alpha in range(0, 256, 16):
                        fade_surface.set_alpha(alpha)
                        screen.blit(fade_surface, (0, 0))
                        pygame.display.flip()
                        pygame.time.delay(20)
                    show = False
                    break

# --- Bomb Logic ---
def draw_bomb(position):
    offset = (SNAKE_SIZE + 10 - SNAKE_SIZE) // 2
    screen.blit(bomb_img, (position[0] - offset, position[1] - offset))

# --- Survival Mode ---
def survival_mode():
    snake, direction, food_position, score = reset_game()
    running = True
    start_ticks = pygame.time.get_ticks()
    particles = []
    bomb_position = None
    bomb_lifetime = 0
    survival_time = 0

    def wrap_position(pos):
        return (pos[0] % WIDTH, pos[1] % HEIGHT)

    def get_new_bomb_position(snake, food_position):
        min_x = 0
        max_x = WIDTH - SNAKE_SIZE
        min_y = 0
        max_y = HEIGHT - SNAKE_SIZE
        while True:
            pos = (
                random.randrange(min_x, max_x + 1, SNAKE_SIZE),
                random.randrange(min_y, max_y + 1, SNAKE_SIZE)
            )
            if pos not in snake and pos != food_position:
                return pos

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, SNAKE_SIZE):
                    direction = (0, -SNAKE_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -SNAKE_SIZE):
                    direction = (0, SNAKE_SIZE)
                elif event.key == pygame.K_LEFT and direction != (SNAKE_SIZE, 0):
                    direction = (-SNAKE_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-SNAKE_SIZE, 0):
                    direction = (SNAKE_SIZE, 0)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Bomb logic: spawn new bomb if needed, decrement lifetime, remove if expired
        if bomb_position is None or bomb_lifetime <= 0 or bomb_position == food_position or bomb_position in snake:
            bomb_position = get_new_bomb_position(snake, food_position)
            bomb_lifetime = random.randint(80, 160)
        else:
            bomb_lifetime -= 1

        new_head = wrap_position((snake[0][0] + direction[0], snake[0][1] + direction[1]))

        # --- Bomb collision: snake dies if touches bomb ---
        if is_on_bomb(new_head, bomb_position):
            # Explosion particle effect
            for _ in range(40):
                particles.append(Particle(
                    bomb_position[0] + SNAKE_SIZE // 2,
                    bomb_position[1] + SNAKE_SIZE // 2,
                    (255, 60, 0)
                ))
            for _ in range(20):
                screen.fill(theme["bg"])
                draw_grid()
                draw_snake(snake)
                draw_food(food_position)
                draw_bomb(bomb_position)
                for p in particles:
                    p.update()
                    p.draw(screen)
                pygame.display.flip()
                beep(1200, 40)
                pygame.time.delay(30)
            particles.clear()
            survival_time = (pygame.time.get_ticks() - start_ticks) // 1000
            name = ""
            input_active = True
            while input_active:
                screen.fill(theme["bg"])
                msg = font.render("Game Over! Enter Name:", True, theme["text"])
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 60))
                name_label = font.render(name + "_", True, theme["text"])
                screen.blit(name_label, (WIDTH//2 - name_label.get_width()//2, HEIGHT//2))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and name:
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                        elif event.unicode.isalnum() and len(name) < 10:
                            name += event.unicode
            update_leaderboard(name, score, survival_time)
            return

        # Usual wall/self collision
        if new_head in snake:
            particle_crash_effect(snake)
            time.sleep(0.5)
            survival_time = (pygame.time.get_ticks() - start_ticks) // 1000
            name = ""
            input_active = True
            while input_active:
                screen.fill(theme["bg"])
                msg = font.render("Game Over! Enter Name:", True, theme["text"])
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 60))
                name_label = font.render(name + "_", True, theme["text"])
                screen.blit(name_label, (WIDTH//2 - name_label.get_width()//2, HEIGHT//2))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and name:
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                        elif event.unicode.isalnum() and len(name) < 10:
                            name += event.unicode
            update_leaderboard(name, score, survival_time)
            return

        snake.insert(0, new_head)

        if is_on_apple(snake[0], food_position):
            score += 10
            food_position = get_new_food_position(snake)
            # Make sure bomb doesn't overlap with new food
            if bomb_position == food_position:
                bomb_position = get_new_bomb_position(snake, food_position)
        else:
            snake.pop()

        screen.fill(theme["bg"])
        draw_grid()
        draw_snake(snake)
        draw_food(food_position)
        if bomb_position:
            draw_bomb(bomb_position)
        score_label = font.render(f"Score: {score}", True, theme["text"])
        score_pos = (10, 10)
        screen.blit(score_label, score_pos)
        length_label = font.render(f"Length: {len(snake)}", True, theme["text"])
        screen.blit(length_label, (10, 40))
        survival_time = (pygame.time.get_ticks() - start_ticks) // 1000
        timer_label = font.render(f"Survival: {survival_time}s", True, theme["text"])
        screen.blit(timer_label, (WIDTH - timer_label.get_width() - 20, 10))

        pygame.display.flip()
        clock.tick(FPS)

# --- Drawing Functions ---
def draw_snake(snake):
    for i, segment in enumerate(snake):
        img = snake_head_img if i == 0 else snake_body_img
        screen.blit(img, segment)

def draw_food(position):
    offset = (SNAKE_SIZE - APPLE_SIZE) // 2
    screen.blit(apple_img, (position[0] + offset, position[1] + offset))

def draw_bomb(position):
    offset = (SNAKE_SIZE + 10 - SNAKE_SIZE) // 2
    screen.blit(bomb_img, (position[0] - offset, position[1] - offset))

def draw_grid():
    grid_color = (50, 50, 80)
    for x in range(0, WIDTH, SNAKE_SIZE):
        pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, SNAKE_SIZE):
        pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))
    scale = 0.25
    block = int(SNAKE_SIZE * scale)
    line1 = "SNAKE(X)"
    line2 = "BY AHMED SAJID"
    width1 = len(line1) * 6 * block
    width2 = len(line2) * 6 * block
    x1 = (WIDTH - width1) // 2
    x2 = (WIDTH - width2) // 2
    y_center = HEIGHT // 2
    y1 = y_center - block * 5
    y2 = y_center + block
    draw_blocky_text_on_grid(line1, x1, y1, (60, 60, 120), scale=scale)
    draw_blocky_text_on_grid(line2, x2, y2, (60, 60, 120), scale=scale)

def draw_blocky_text_on_grid(message, start_x, start_y, color=(80, 80, 180), scale=0.5):
    font_map = {
        "A": ["01110","10001","11111","10001","10001"],
        "E": ["11111","10000","11110","10000","11111"],
        "G": ["01111","10000","10111","10001","01110"],
        "H": ["10001","10001","11111","10001","10001"],
        "I": ["11111","00100","00100","00100","11111"],
        "J": ["00111","00010","00010","10010","01100"],
        "K": ["10001","10010","11100","10010","10001"],
        "M": ["10001","11011","10101","10001","10001"],
        "N": ["10001","11001","10101","10011","10001"],
        "S": ["01111","10000","01110","00001","11110"],
        "D": ["11110","10001","10001","10001","11110"],
        "B": ["11110","10001","11110","10001","11110"],
        "Y": ["10001","01010","00100","00100","00100"],
        " ": ["00000","00000","00000","00000","00000"],
    }
    message = message.upper()
    x = start_x
    y = start_y
    block = int(SNAKE_SIZE * scale)
    for char in message:
        if (char in font_map):
            pattern = font_map[char]
            for row_idx, row in enumerate(pattern):
                for col_idx, bit in enumerate(row):
                    if bit == "1":
                        rect = pygame.Rect(
                            x + col_idx * block,
                            y + row_idx * block,
                            block, block
                        )
                        pygame.draw.rect(screen, color, rect)
            x += int(6 * block)
        else:
            x += int(6 * block)

# --- Game Logic ---
def reset_game():
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (0, -SNAKE_SIZE)
    food_position = get_new_food_position(snake)
    score = 0
    return snake, direction, food_position, score

def score_pixel_animation(score, pos, particles):
    color = (255, 215, 0) if score % 100 == 0 else (0, 255, 255)
    for _ in range(40):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 7)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        particles.append({
            "x": pos[0], "y": pos[1],
            "vx": vx, "vy": vy,
            "life": random.randint(12, 20),
            "color": color
        })
    for _ in range(18):
        screen.fill(theme["bg"])
        score_label = font.render(f"Score: {score}", True, theme["text"])
        screen.blit(score_label, pos)
        for p in particles:
            if p["life"] > 0:
                pygame.draw.rect(screen, p["color"], (int(p["x"]), int(p["y"]), 5, 5))
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["life"] -= 1
        pygame.display.flip()
        pygame.time.delay(18)

def load_high_score():
    try:
        with open("high_score.txt", "r") as f:
            return int(f.read())
    except Exception:
        return 0

def save_high_score(high_score):
    with open("high_score.txt", "w") as f:
        f.write(str(high_score))

def countdown():
    for i in range(3, 0, -1):
        screen.fill(theme["bg"])
        label = font.render(f"Starting in {i}", True, theme["text"])
        screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - label.get_height()//2))
        pygame.display.flip()
        pygame.time.delay(800)

# --- Background Music Playlist Setup ---
MUSIC_DIR = r"C:\Users\notye\OneDrive\Documents\Python Projects by me\snake-game\src\assets\sounds\Music"
music_files = []
current_music_index = 0

def load_music_playlist():
    global music_files
    music_files = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
    music_files.sort()

def is_music_available():
    return bool(music_files)

def play_music(index=0):
    if not is_music_available():
        return
    try:
        pygame.mixer.music.load(music_files[index])
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
    except Exception as e:
        print(f"Error playing music: {e}")

def play_next_music():
    global current_music_index
    if not is_music_available():
        return
    current_music_index = (current_music_index + 1) % len(music_files)
    play_music(current_music_index)

def start_music():
    global current_music_index
    if not is_music_available():
        return
    current_music_index = 0
    play_music(current_music_index)

def stop_music():
    pygame.mixer.music.stop()

pygame.mixer.init()
load_music_playlist()

# --- Main Loop ---
def main():
    def wrap_position(pos):
        return (pos[0] % WIDTH, pos[1] % HEIGHT)

    def get_new_bomb_position(snake, food_position):
        min_x = 0
        max_x = WIDTH - SNAKE_SIZE
        min_y = 0
        max_y = HEIGHT - SNAKE_SIZE
        while True:
            pos = (
                random.randrange(min_x, max_x + 1, SNAKE_SIZE),
                random.randrange(min_y, max_y + 1, SNAKE_SIZE)
            )
            if pos not in snake and pos != food_position:
                return pos

    startup_screen()
    snake, direction, food_position, score = reset_game()
    running = False
    high_score = load_high_score()
    last_milestone = 0
    particles = []

    while True:
        choice = home_screen()
        if choice == "Play New Game":
            snake, direction, food_position, score = reset_game()
            running = True
            last_milestone = 0
            particles = []
            start_music()
        elif choice == "Resume" and running:
            pass
        elif choice == "Help and Licensing":
            help_and_licensing_screen()
            continue
        elif choice == "Settings":
            settings_screen()
            continue
        elif choice == "Send us Feedback":
            feedback_screen()
            continue
        elif choice == "Leaderboard":
            leaderboard_screen()
            continue
        elif choice == "Challenges":
            challenges_screen()
            continue
        elif choice == "Quit":
            pygame.quit(); exit()
        else:
            continue

        start_ticks = pygame.time.get_ticks()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                elif event.type == pygame.USEREVENT + 1:
                    play_next_music()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != (0, SNAKE_SIZE):
                        direction = (0, -SNAKE_SIZE)
                    elif event.key == pygame.K_DOWN and direction != (0, -SNAKE_SIZE):
                        direction = (0, SNAKE_SIZE)
                    elif event.key == pygame.K_LEFT and direction != (SNAKE_SIZE, 0):
                        direction = (-SNAKE_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-SNAKE_SIZE, 0):
                        direction = (SNAKE_SIZE, 0)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_p:
                        result = pause_screen()
                        if result == "Return to Menu":
                            running = False
                            break

            new_head = wrap_position((snake[0][0] + direction[0], snake[0][1] + direction[1]))

            if new_head in snake:
                play_sound('gameover')
                particle_crash_effect(snake)
                time.sleep(0.5)
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                result = end_game_screen(score, high_score)
                if result == "Play Again":
                    snake, direction, food_position, score = reset_game()
                    start_ticks = pygame.time.get_ticks()
                    last_milestone = 0
                    continue
                elif result == "Return to Menu":
                    running = False
                    break

            snake.insert(0, new_head)

            if is_on_apple(snake[0], food_position):
                score += 10
                food_position = get_new_food_position(snake)
                play_sound('eat')
            else:
                snake.pop()

            screen.fill(theme["bg"])
            draw_grid()
            draw_snake(snake)
            draw_food(food_position)
            score_label = font.render(f"Score: {score}", True, theme["text"])
            score_pos = (10, 10)
            screen.blit(score_label, score_pos)
            length_label = font.render(f"Length: {len(snake)}", True, theme["text"])
            screen.blit(length_label, (10, 40))
            draw_timer(start_ticks)

            if score > 0 and score % 100 == 0 and score != last_milestone:
                score_pixel_animation(score, (score_pos[0] + 100, score_pos[1] + 20), particles)
                last_milestone = score

            for p in particles[:]:
                if p["life"] > 0:
                    pygame.draw.rect(screen, p["color"], (int(p["x"]), int(p["y"]), 5, 5))
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["life"] -= 1
                else:
                    particles.remove(p)

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()
