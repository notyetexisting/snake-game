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
    import winsound  # pylint: disable=import-error
    def beep(freq, dur):
        try:
            winsound.Beep(freq, dur)
        except RuntimeError:
            pass
else:
    def beep(freq, dur):
        pass

pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Constants ---
WIDTH, HEIGHT = 704, 704
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
        font_path = os.path.join(BASE_DIR, font_file)
        try:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
            else:
                print(f"Warning: Font file '{font_file}' not found in current directory. Using default font.")
                return pygame.font.SysFont(None, size)
        except Exception as e:
            print(f"Error loading font '{font_file}': {e}")
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

snake_head_img = load_and_scale(os.path.join(BASE_DIR, "snake_head.png"), SNAKE_SIZE)
snake_body_img = load_and_scale(os.path.join(BASE_DIR, "snake_body.png"), SNAKE_SIZE)
apple_img = load_and_scale(os.path.join(BASE_DIR, "food.png"), APPLE_SIZE)
bomb_img = load_and_scale(os.path.join(BASE_DIR, "Bomb.png"), SNAKE_SIZE + 10)

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

def game_over_name_entry(score, survival_time):
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
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum() and len(name) < 10:
                    name += event.unicode
    update_leaderboard(name, score, survival_time)

# --- Particle Effect ---
particles = []
def create_particle(x, y, color):
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(2, 6)
    return {
        "x": x, "y": y,
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,
        "life": random.randint(10, 20),
        "color": color
    }

def particle_crash_effect(snake, session=None):
    global particles
    for segment in snake:
        for _ in range(12):
            particles.append(create_particle(segment[0] + SNAKE_SIZE // 2, segment[1] + SNAKE_SIZE // 2, theme["snake"]))
    for _ in range(20):
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        temp_surf = pygame.Surface((WIDTH, HEIGHT))
        temp_surf.fill(theme["bg"])
        if session:
            draw_grid(obstacles=session.obstacles, surface=temp_surf)
            draw_snake(session.snake, surface=temp_surf)
            if session.is_multiplayer: draw_snake(session.snake2, player=2, surface=temp_surf)
            draw_food(session.food_position, surface=temp_surf)

        for p in particles[:]:
            if p["life"] > 0:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["life"] -= 1
                pygame.draw.circle(temp_surf, p["color"], (int(p["x"]), int(p["y"])), 4)
            else:
                particles.remove(p)
        screen.fill((0, 0, 0))
        screen.blit(temp_surf, (offset_x, offset_y))
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
        ("Resume", pygame.Rect(60, 100, 240, 50)),
        ("Play New Game", pygame.Rect(60, 165, 240, 50)),
        ("Multiplayer", pygame.Rect(60, 230, 240, 50)),
        ("Challenges", pygame.Rect(60, 295, 240, 50)),
        ("Leaderboard", pygame.Rect(60, 360, 240, 50)),
        ("Settings", pygame.Rect(60, 425, 240, 50)),
        ("Help and Licensing", pygame.Rect(60, 490, 240, 50)),
        ("Send us Feedback", pygame.Rect(60, 555, 240, 50)),
        ("Quit", pygame.Rect(60, 620, 240, 50)),
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
                pygame.quit(); sys.exit()
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
    # Ensure all sizes are multiples of SNAKE_SIZE (32)
    sizes = [(640, 640), (704, 704), (800, 640), (896, 704), (1024, 768)]
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
                pygame.quit(); sys.exit()
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
                pygame.quit(); sys.exit()
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
                pygame.quit(); sys.exit()
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
        ("Survival Mode", pygame.Rect(WIDTH//2-120, 180, 240, 60)),
        ("Walls of Doom", pygame.Rect(WIDTH//2-120, 260, 240, 60)),
        ("Speed Run", pygame.Rect(WIDTH//2-120, 340, 240, 60)),
        ("Back", pygame.Rect(WIDTH//2-120, 420, 240, 60)),
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
                pygame.quit(); sys.exit()
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
                pygame.quit(); sys.exit()
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
                pygame.quit(); sys.exit()
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
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    for alpha in range(0, 256, 16):
                        fade_surface.set_alpha(alpha)
                        screen.blit(fade_surface, (0, 0))
                        pygame.display.flip()
                        pygame.time.delay(20)
                    show = False
                    break

# --- Unified Game Play Function ---
def play_game(session):
    global FPS, WIDTH, HEIGHT, screen, font, theme
    mode = session.mode
    is_survival = (mode == "Survival")

    if session.paused_at > 0:
        session.total_paused_time += (pygame.time.get_ticks() - session.paused_at)
        session.paused_at = 0

    high_score = 0
    if not is_survival:
        if not pygame.mixer.music.get_busy():
            start_music()
        high_score = load_high_score()

    snake = session.snake
    direction = session.direction
    food_position = session.food_position
    score = session.score

    snake2 = session.snake2
    direction2 = session.direction2
    score2 = session.score2

    start_ticks = session.start_ticks
    last_milestone = session.last_milestone
    particles = session.particles
    bomb_position = session.bomb_position
    bomb_lifetime = session.bomb_lifetime
    running = True

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
        new_head2 = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.USEREVENT + 1 and not is_survival:
                play_next_music()
            elif event.type == pygame.KEYDOWN:
                # Player 1 Controls
                if event.key == pygame.K_UP and direction != (0, SNAKE_SIZE):
                    direction = (0, -SNAKE_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -SNAKE_SIZE):
                    direction = (0, SNAKE_SIZE)
                elif event.key == pygame.K_LEFT and direction != (SNAKE_SIZE, 0):
                    direction = (-SNAKE_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-SNAKE_SIZE, 0):
                    direction = (SNAKE_SIZE, 0)

                # Player 2 Controls
                if session.is_multiplayer:
                    if event.key == pygame.K_w and direction2 != (0, SNAKE_SIZE):
                        direction2 = (0, -SNAKE_SIZE)
                    elif event.key == pygame.K_s and direction2 != (0, -SNAKE_SIZE):
                        direction2 = (0, SNAKE_SIZE)
                    elif event.key == pygame.K_a and direction2 != (SNAKE_SIZE, 0):
                        direction2 = (-SNAKE_SIZE, 0)
                    elif event.key == pygame.K_d and direction2 != (-SNAKE_SIZE, 0):
                        direction2 = (SNAKE_SIZE, 0)

                elif event.key == pygame.K_ESCAPE:
                    running = False
                    session.paused_at = pygame.time.get_ticks()
                    session.snake = snake
                    session.direction = direction
                    session.food_position = food_position
                    session.score = score
                    session.last_milestone = last_milestone
                    session.particles = particles
                    session.bomb_position = bomb_position
                    session.bomb_lifetime = bomb_lifetime
                elif event.key == pygame.K_p and not is_survival:
                    pause_start = pygame.time.get_ticks()
                    result = pause_screen()
                    session.total_paused_time += (pygame.time.get_ticks() - pause_start)
                    if result == "Return to Menu":
                        running = False
                        session.paused_at = pygame.time.get_ticks()
                        session.snake = snake
                        session.direction = direction
                        session.food_position = food_position
                        session.score = score
                        session.last_milestone = last_milestone
                        session.particles = particles
                        session.bomb_position = bomb_position
                        session.bomb_lifetime = bomb_lifetime
                        return
                elif event.key == pygame.K_r and not is_survival:
                    # Resume from pause if R pressed (handled in pause_screen too)
                    pass

        if is_survival:
            if bomb_position is None or bomb_lifetime <= 0 or bomb_position == food_position or bomb_position in snake:
                bomb_position = get_new_bomb_position(snake, food_position)
                bomb_lifetime = random.randint(80, 160)
            else:
                bomb_lifetime -= 1

        new_head = wrap_position((snake[0][0] + direction[0], snake[0][1] + direction[1]))
        if session.is_multiplayer:
            new_head2 = wrap_position((snake2[0][0] + direction2[0], snake2[0][1] + direction2[1]))

        # Obstacle collision
        if new_head in session.obstacles:
            play_sound('gameover')
            particle_crash_effect(snake, session=session)
            running = False
            continue
        if session.is_multiplayer and new_head2 in session.obstacles:
            play_sound('gameover')
            particle_crash_effect(snake2, session=session)
            running = False
            continue

        if is_survival and is_on_bomb(new_head, bomb_position):
            for _ in range(40):
                particles.append(create_particle(bomb_position[0] + SNAKE_SIZE // 2, bomb_position[1] + SNAKE_SIZE // 2, (255, 60, 0)))
            for _ in range(20):
                offset_x = random.randint(-8, 8)
                offset_y = random.randint(-8, 8)
                temp_surf = pygame.Surface((WIDTH, HEIGHT))
                temp_surf.fill(theme["bg"])
                draw_grid(obstacles=session.obstacles); draw_snake(snake); draw_food(food_position); draw_bomb(bomb_position)
                for p in particles[:]:
                    if p["life"] > 0:
                        p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1
                        pygame.draw.circle(temp_surf, p["color"], (int(p["x"]), int(p["y"])), 4)
                    else:
                        particles.remove(p)
                screen.fill((0, 0, 0))
                screen.blit(temp_surf, (offset_x, offset_y))
                pygame.display.flip()
                beep(1200, 40); pygame.time.delay(30)
            particles.clear()
            game_over_name_entry(score, (pygame.time.get_ticks() - start_ticks) // 1000)
            return

        # Player 1 Collisions
        if new_head in snake or (session.is_multiplayer and new_head in snake2):
            play_sound('gameover')
            particle_crash_effect(snake, session=session)
            if is_survival:
                game_over_name_entry(score, (pygame.time.get_ticks() - start_ticks - session.total_paused_time) // 1000)
                return
            elif session.is_multiplayer:
                result = end_game_screen(score, score2) # Reuse end_game_screen to show scores
                if result == "Play Again":
                    session.snake, session.direction, session.food_position, session.score = reset_game()
                    session.snake2 = [(WIDTH // 2, HEIGHT // 2 + SNAKE_SIZE * 2)]
                    session.direction2 = (0, SNAKE_SIZE)
                    session.score2 = 0
                    snake, direction, food_position, score = session.snake, session.direction, session.food_position, session.score
                    snake2, direction2, score2 = session.snake2, session.direction2, session.score2
                    start_ticks = pygame.time.get_ticks()
                    session.total_paused_time = 0
                    continue
                else: return
            else:
                if score > high_score: save_high_score(score)
                result = end_game_screen(score, high_score)
                if result == "Play Again":
                    snake, direction, food_position, score = reset_game()
                    start_ticks = pygame.time.get_ticks()
                    session.total_paused_time = 0
                    last_milestone = 0
                    continue
                else: return

        # Player 2 Collisions
        if session.is_multiplayer and (new_head2 in snake2 or new_head2 in snake):
            play_sound('gameover')
            particle_crash_effect(snake2, session=session)
            result = end_game_screen(score, score2)
            if result == "Play Again":
                session.snake, session.direction, session.food_position, session.score = reset_game()
                session.snake2 = [(WIDTH // 2, HEIGHT // 2 + SNAKE_SIZE * 2)]
                session.direction2 = (0, SNAKE_SIZE)
                session.score2 = 0
                snake, direction, food_position, score = session.snake, session.direction, session.food_position, session.score
                snake2, direction2, score2 = session.snake2, session.direction2, session.score2
                start_ticks = pygame.time.get_ticks()
                session.total_paused_time = 0
                continue
            else: return

        snake.insert(0, new_head)
        if session.is_multiplayer: snake2.insert(0, new_head2)

        # Eating Food
        ate_p1 = is_on_apple(snake[0], food_position)
        ate_p2 = session.is_multiplayer and is_on_apple(snake2[0], food_position)

        if ate_p1 or ate_p2:
            now = pygame.time.get_ticks()
            if now - session.last_eat_time < 3000:
                session.multiplier = min(session.multiplier + 1, 5)
            else:
                session.multiplier = 1
            session.last_eat_time = now

            if ate_p1: score += 10 * session.multiplier
            else: score2 += 10 * session.multiplier

            # Use all snake segments for new food pos
            all_segments = snake + (snake2 if session.is_multiplayer else [])
            food_position = get_new_food_position(all_segments)
            play_sound('eat')
            if is_survival and bomb_position == food_position:
                bomb_position = get_new_bomb_position(all_segments, food_position)

            # Animation for eating
            for _ in range(15):
                particles.append(create_particle(food_position[0], food_position[1], theme["food"]))
        else:
            snake.pop()
            if session.is_multiplayer: snake2.pop()

        screen.fill(theme["bg"])
        draw_grid(obstacles=session.obstacles)
        draw_snake(snake, player=1, multiplier=session.multiplier)
        if session.is_multiplayer: draw_snake(snake2, player=2, multiplier=session.multiplier)

        pulse = math.sin(pygame.time.get_ticks() / 200) * 4
        draw_food(food_position, pulse=pulse)
        if is_survival and bomb_position:
            draw_bomb(bomb_position)

        score_label = font.render(f"P1 Score: {score}", True, theme["text"])
        screen.blit(score_label, (10, 10))
        if session.is_multiplayer:
            score_label2 = font.render(f"P2 Score: {score2}", True, (100, 255, 255))
            screen.blit(score_label2, (10, 40))
            mult_label = font.render(f"Multiplier: x{session.multiplier}", True, theme["text"])
            screen.blit(mult_label, (10, 70))
        else:
            length_label = font.render(f"Length: {len(snake)}", True, theme["text"])
            screen.blit(length_label, (10, 40))
            if session.multiplier > 1:
                mult_label = font.render(f"Multiplier: x{session.multiplier}", True, (255, 255, 0))
                screen.blit(mult_label, (10, 70))

        if is_survival:
            survival_time = (pygame.time.get_ticks() - start_ticks - session.total_paused_time) // 1000
            timer_label = font.render(f"Survival: {survival_time}s", True, theme["text"])
            screen.blit(timer_label, (WIDTH - timer_label.get_width() - 20, 10))
        elif session.mode == "Speed Run":
            remaining = (session.game_duration - (pygame.time.get_ticks() - start_ticks - session.total_paused_time)) // 1000
            if remaining <= 0:
                running = False
                end_game_screen(score, high_score)
                return
            timer_label = font.render(f"Time: {remaining}s", True, (255, 100, 100))
            screen.blit(timer_label, (WIDTH - timer_label.get_width() - 20, 10))
        else:
            # For Normal mode, draw_timer needs to account for paused time too
            elapsed = (pygame.time.get_ticks() - start_ticks - session.total_paused_time) // 1000
            mins = elapsed // 60
            secs = elapsed % 60
            timer_label = font.render(f"Time: {mins:02}:{secs:02}", True, theme["text"])
            screen.blit(timer_label, (WIDTH - timer_label.get_width() - 20, 10))
            if score > 0 and score % 100 == 0 and score != last_milestone:
                score_pixel_animation(score, (110, 30), particles)
                last_milestone = score

        for p in particles[:]:
            if p["life"] > 0:
                pygame.draw.rect(screen, p["color"], (int(p["x"]), int(p["y"]), 5, 5))
                p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1
            else:
                particles.remove(p)

        # Update session state for persistence
        session.snake = snake
        session.direction = direction
        session.score = score
        if session.is_multiplayer:
            session.snake2 = snake2
            session.direction2 = direction2
            session.score2 = score2
        session.food_position = food_position
        session.bomb_position = bomb_position
        session.bomb_lifetime = bomb_lifetime

        pygame.display.flip()
        clock.tick(FPS)


# --- Drawing Functions ---
def draw_snake(snake, player=1, multiplier=1, surface=None):
    if surface is None: surface = screen
    for i, segment in enumerate(snake):
        if player == 1:
            img = snake_head_img if i == 0 else snake_body_img
            if multiplier > 1:
                # Tint based on multiplier
                tint = (min(255, 200 + multiplier*10), 255 - min(255, multiplier*40), 255 - min(255, multiplier*40))
                img = img.copy()
                img.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
        else:
            # Simple tint for Player 2 (Cyan-ish)
            img = snake_head_img.copy() if i == 0 else snake_body_img.copy()
            img.fill((100, 255, 255), special_flags=pygame.BLEND_RGB_MULT)
        surface.blit(img, segment)

def draw_food(position, pulse=0, surface=None):
    if surface is None: surface = screen
    offset = (SNAKE_SIZE - APPLE_SIZE) // 2
    if pulse != 0:
        size = int(APPLE_SIZE + pulse)
        img = pygame.transform.smoothscale(apple_img, (max(1, size), max(1, size)))
        new_offset = (SNAKE_SIZE - size) // 2
        surface.blit(img, (position[0] + new_offset, position[1] + new_offset))
    else:
        surface.blit(apple_img, (position[0] + offset, position[1] + offset))

def draw_bomb(position, surface=None):
    if surface is None: surface = screen
    offset = (SNAKE_SIZE + 10 - SNAKE_SIZE) // 2
    surface.blit(bomb_img, (position[0] - offset, position[1] - offset))

def draw_grid(obstacles=None, surface=None):
    if surface is None: surface = screen
    grid_color = (50, 50, 80)
    for x in range(0, WIDTH, SNAKE_SIZE):
        pygame.draw.line(surface, grid_color, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, SNAKE_SIZE):
        pygame.draw.line(surface, grid_color, (0, y), (WIDTH, y))

    if obstacles:
        for obs in obstacles:
            pygame.draw.rect(surface, (150, 150, 150), (obs[0]+2, obs[1]+2, SNAKE_SIZE-4, SNAKE_SIZE-4), border_radius=4)
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
    draw_blocky_text_on_grid(line1, x1, y1, (60, 60, 120), scale=scale, surface=surface)
    draw_blocky_text_on_grid(line2, x2, y2, (60, 60, 120), scale=scale, surface=surface)

def draw_blocky_text_on_grid(message, start_x, start_y, color=(80, 80, 180), scale=0.5, surface=None):
    if surface is None: surface = screen
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
                        pygame.draw.rect(surface, color, rect)
            x += int(6 * block)
        else:
            x += int(6 * block)

# --- Game Logic ---
class GameSession:
    def __init__(self, mode="Normal"):
        self.mode = mode
        self.snake, self.direction, self.food_position, self.score = reset_game()
        self.is_multiplayer = (mode == "Multiplayer")
        if self.is_multiplayer:
            self.snake2 = [(WIDTH // 2, HEIGHT // 2 + SNAKE_SIZE * 2)]
            self.direction2 = (0, SNAKE_SIZE)
            self.score2 = 0
        else:
            self.snake2 = None
            self.direction2 = None
            self.score2 = 0
        self.obstacles = []
        if mode == "Walls":
            self.generate_obstacles()
        self.game_duration = 60000 if mode == "Speed Run" else 0
        self.start_ticks = pygame.time.get_ticks()
        self.last_milestone = 0
        self.particles = []
        self.bomb_position = None
        self.bomb_lifetime = 0
        self.paused_at = 0
        self.total_paused_time = 0
        self.multiplier = 1
        self.last_eat_time = 0

    def generate_obstacles(self):
        self.obstacles = []
        for _ in range(10):
            while True:
                pos = (
                    random.randrange(0, WIDTH, SNAKE_SIZE),
                    random.randrange(0, HEIGHT, SNAKE_SIZE)
                )
                if pos not in self.snake and pos != self.food_position:
                    self.obstacles.append(pos)
                    break

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
MUSIC_DIR = BASE_DIR
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
    startup_screen()
    current_session = None

    while True:
        choice = home_screen()
        if choice == "Play New Game":
            current_session = GameSession(mode="Normal")
            play_game(current_session)
        elif choice == "Multiplayer":
            current_session = GameSession(mode="Multiplayer")
            play_game(current_session)
        elif choice == "Resume":
            if current_session:
                play_game(current_session)
            else:
                current_session = GameSession(mode="Normal")
                play_game(current_session)
        elif choice == "Help and Licensing":
            help_and_licensing_screen()
        elif choice == "Settings":
            settings_screen()
        elif choice == "Send us Feedback":
            feedback_screen()
        elif choice == "Leaderboard":
            leaderboard_screen()
        elif choice == "Challenges":
            res = challenges_screen()
            if res == "Survival Mode":
                current_session = GameSession(mode="Survival")
                play_game(current_session)
            elif res == "Walls of Doom":
                current_session = GameSession(mode="Walls")
                play_game(current_session)
            elif res == "Speed Run":
                current_session = GameSession(mode="Speed Run")
                play_game(current_session)
        elif choice == "Quit":
            pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()
