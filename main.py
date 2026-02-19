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

def get_theme_font(t_name, size=36):
    font_file = THEMES[t_name].get("font")
    if font_file:
        font_path = os.path.join(BASE_DIR, font_file)
        try:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
            print(f"Warning: Font file '{font_file}' not found. Using default.")
            return pygame.font.SysFont(None, size)
        except (pygame.error, OSError) as e:
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
        img_rect = img.get_rect()
        scale_factor = min(size / img_rect.width, size / img_rect.height)
        new_width = int(img_rect.width * scale_factor)
        new_height = int(img_rect.height * scale_factor)
        img = pygame.transform.smoothscale(img, (new_width, new_height))
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.blit(img, ((size - new_width) // 2, (size - new_height) // 2))
        return surface
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading image at '{path}': {e}")
        return pygame.Surface((size, size), pygame.SRCALPHA)

snake_head_img = load_and_scale(os.path.join(BASE_DIR, "snake_head.png"), SNAKE_SIZE)
snake_body_img = load_and_scale(os.path.join(BASE_DIR, "snake_body.png"), SNAKE_SIZE)
apple_img = load_and_scale(os.path.join(BASE_DIR, "food.png"), APPLE_SIZE)
bomb_img = load_and_scale(os.path.join(BASE_DIR, "Bomb.png"), SNAKE_SIZE + 10)

# --- Leaderboard Management ---
LEADERBOARD_FILE = "survival_leaderboard.json"

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def save_leaderboard(leaderboard):
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(leaderboard, f)
    except OSError as e:
        print(f"Error saving leaderboard: {e}")

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

# --- High Score ---
def load_high_score():
    try:
        with open("highscore.txt", "r", encoding="utf-8") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError, OSError):
        return 0

def save_high_score(h_score):
    try:
        with open("highscore.txt", "w", encoding="utf-8") as f:
            f.write(str(h_score))
    except OSError:
        pass

# --- Particle Effect ---
particles = []

def create_particle(x, y, p_color):
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(2, 6)
    return {
        "x": x, "y": y,
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,
        "life": random.randint(10, 20),
        "color": p_color
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
            draw_snake(session.snake, player=1, surface=temp_surf)
            if session.is_multiplayer:
                draw_snake(session.snake2, player=2, surface=temp_surf)
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

def get_new_food_position(snake, obstacles=None):
    while True:
        pos = (
            random.randrange(0, WIDTH, SNAKE_SIZE),
            random.randrange(0, HEIGHT, SNAKE_SIZE)
        )
        if pos not in snake:
            if obstacles is None or pos not in obstacles:
                return pos

def get_new_bomb_position(snake, food_pos, obstacles=None):
    while True:
        pos = (
            random.randrange(0, WIDTH, SNAKE_SIZE),
            random.randrange(0, HEIGHT, SNAKE_SIZE)
        )
        if pos not in snake and pos != food_pos:
            if obstacles is None or pos not in obstacles:
                return pos

def is_on_apple(s_head, f_pos):
    offset = (SNAKE_SIZE - APPLE_SIZE) // 2
    apple_center = (f_pos[0] + offset + APPLE_SIZE // 2, f_pos[1] + offset + APPLE_SIZE // 2)
    snake_center = (s_head[0] + SNAKE_SIZE // 2, s_head[1] + SNAKE_SIZE // 2)
    return (abs(snake_center[0] - apple_center[0]) < SNAKE_SIZE // 2) and \
           (abs(snake_center[1] - apple_center[1]) < SNAKE_SIZE // 2)

def is_on_bomb(s_head, b_pos):
    offset = (SNAKE_SIZE + 10 - SNAKE_SIZE) // 2
    bomb_center = (b_pos[0] + offset + (SNAKE_SIZE + 10) // 2, b_pos[1] + offset + (SNAKE_SIZE + 10) // 2)
    snake_center = (s_head[0] + SNAKE_SIZE // 2, s_head[1] + SNAKE_SIZE // 2)
    return (abs(snake_center[0] - bomb_center[0]) < SNAKE_SIZE // 2) and \
           (abs(snake_center[1] - bomb_center[1]) < SNAKE_SIZE // 2)

def set_theme(new_t_name):
    global theme_name, theme, font
    theme_name = new_t_name
    theme = THEMES[theme_name]
    font = get_theme_font(theme_name, 36)

def draw_snake(snake, player=1, multiplier=1, surface=None):
    if surface is None: surface = screen
    for i, segment in enumerate(snake):
        if player == 1:
            img = snake_head_img if i == 0 else snake_body_img
            if multiplier > 1:
                tint = (min(255, 200 + multiplier*10), 255 - min(255, multiplier*40), 255 - min(255, multiplier*40))
                img = img.copy()
                img.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
        else:
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

def draw_blocky_text_on_grid(msg, start_x, start_y, color=(80, 80, 180), scale=0.5, surface=None):
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
    msg = msg.upper()
    x = start_x
    y = start_y
    block = int(SNAKE_SIZE * scale)
    for char in msg:
        if char in font_map:
            pattern = font_map[char]
            for row_idx, row in enumerate(pattern):
                for col_idx, bit in enumerate(row):
                    if bit == "1":
                        rect = pygame.Rect(x + col_idx * block, y + row_idx * block, block, block)
                        pygame.draw.rect(surface, color, rect)
            x += int(6 * block)
        else:
            x += int(6 * block)

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
    sc = 0.25
    bl = int(SNAKE_SIZE * sc)
    l1, l2 = "SNAKE(X)", "BY AHMED SAJID"
    x1, x2 = (WIDTH - len(l1)*6*bl)//2, (WIDTH - len(l2)*6*bl)//2
    yc = HEIGHT // 2
    draw_blocky_text_on_grid(l1, x1, yc - bl*5, (60, 60, 120), scale=sc, surface=surface)
    draw_blocky_text_on_grid(l2, x2, yc + bl, (60, 60, 120), scale=sc, surface=surface)

def score_pixel_animation(score, pos, p_list):
    color = (255, 215, 0) if score % 100 == 0 else (0, 255, 255)
    for _ in range(40):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 7)
        p_list.append({
            "x": pos[0], "y": pos[1],
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(12, 20),
            "color": color
        })
    for _ in range(18):
        screen.fill(theme["bg"])
        s_label = font.render(f"Score: {score}", True, theme["text"])
        screen.blit(s_label, pos)
        for p in p_list:
            if p["life"] > 0:
                pygame.draw.rect(screen, p["color"], (int(p["x"]), int(p["y"]), 5, 5))
                p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1
        pygame.display.flip()
        pygame.time.delay(18)

# --- Game Logic ---
class GameSession:
    def __init__(self, mode="Normal"):
        self.mode = mode
        self.snake = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = (0, -SNAKE_SIZE)
        self.food_position = get_new_food_position(self.snake)
        self.score = 0
        self.is_multiplayer = (mode == "Multiplayer")
        if self.is_multiplayer:
            self.snake2 = [(WIDTH // 2, HEIGHT // 2 + SNAKE_SIZE * 2)]
            self.direction2 = (0, SNAKE_SIZE)
            self.score2 = 0
        else:
            self.snake2, self.direction2, self.score2 = None, None, 0
        self.obstacles = []
        if mode == "Walls": self.generate_obstacles()
        self.game_duration = 60000 if mode == "Speed Run" else 0
        self.start_ticks = pygame.time.get_ticks()
        self.last_milestone = 0
        self.particles = []
        self.bomb_position, self.bomb_lifetime = None, 0
        self.paused_at, self.total_paused_time = 0, 0
        self.multiplier, self.last_eat_time = 1, 0

    def generate_obstacles(self):
        for _ in range(10):
            while True:
                pos = (random.randrange(0, WIDTH, SNAKE_SIZE), random.randrange(0, HEIGHT, SNAKE_SIZE))
                if pos not in self.snake and pos != self.food_position:
                    self.obstacles.append(pos); break

# --- Screens ---
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
    sel = 1
    while True:
        screen.fill(theme["bg"])
        title = font.render("SNAKE(X) BY AHMED SAJID", True, theme["text"])
        screen.blit(title, (30, 40))
        for i, (txt, rect) in enumerate(buttons): draw_button(rect, txt, active=(i == sel))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: sel = (sel - 1) % len(buttons)
                elif event.key == pygame.K_DOWN: sel = (sel + 1) % len(buttons)
                elif event.key == pygame.K_RETURN: return buttons[sel][0]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (_, rect) in enumerate(buttons):
                    if rect.collidepoint(event.pos): return buttons[i][0]

def settings_screen():
    global FPS, theme_name, theme, sound_on, font, WIDTH, HEIGHT, screen
    t_list = list(THEMES.keys())
    t_idx = t_list.index(theme_name)
    sizes = [(640, 640), (704, 704), (800, 640), (896, 704), (1024, 768)]
    s_idx = [i for i, s in enumerate(sizes) if s == (WIDTH, HEIGHT)]
    s_idx = s_idx[0] if s_idx else 1
    opts = ["Speed (FPS):", "Theme:", "Sound:", "Screen Size:", "Back"]
    sel, editing = 0, False
    while True:
        screen.fill(theme["bg"])
        title = font.render("Settings", True, theme["text"])
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        for i, opt in enumerate(opts):
            y = 160 + i*80
            val = f"{FPS}" if opt == "Speed (FPS):" else t_list[t_idx] if opt == "Theme:" else \
                  ("On" if sound_on else "Off") if opt == "Sound:" else \
                  f"{sizes[s_idx][0]}x{sizes[s_idx][1]}" if opt == "Screen Size:" else ""
            rect = pygame.Rect(WIDTH//2-150, y-10, 300, 60)
            if i == sel: pygame.draw.rect(screen, (80, 80, 180), rect, border_radius=12)
            label = font.render(f"{opt} {val}", True, (255,255,0) if i == sel else theme["text"])
            screen.blit(label, (WIDTH//2 - label.get_width()//2, y))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not editing:
                    if event.key == pygame.K_UP: sel = (sel - 1) % len(opts)
                    elif event.key == pygame.K_DOWN: sel = (sel + 1) % len(opts)
                    elif event.key == pygame.K_RETURN:
                        if opts[sel] == "Back": return
                        editing = True
                else:
                    if event.key == pygame.K_LEFT:
                        if opts[sel] == "Speed (FPS):": FPS = max(5, FPS - 1)
                        elif opts[sel] == "Theme:": t_idx = (t_idx - 1) % len(t_list); set_theme(t_list[t_idx])
                        elif opts[sel] == "Sound:": sound_on = not sound_on
                        elif opts[sel] == "Screen Size:": s_idx = (s_idx - 1) % len(sizes)
                    elif event.key == pygame.K_RIGHT:
                        if opts[sel] == "Speed (FPS):": FPS = min(60, FPS + 1)
                        elif opts[sel] == "Theme:": t_idx = (t_idx + 1) % len(t_list); set_theme(t_list[t_idx])
                        elif opts[sel] == "Sound:": sound_on = not sound_on
                        elif opts[sel] == "Screen Size:": s_idx = (s_idx + 1) % len(sizes)
                    elif event.key == pygame.K_RETURN:
                        if opts[sel] == "Screen Size:":
                            WIDTH, HEIGHT = sizes[s_idx]; screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        editing = False
                    elif event.key == pygame.K_ESCAPE: editing = False

def pause_screen():
    btns = [("Resume", pygame.Rect(WIDTH//2-100, 320, 200, 50)), ("Return to Menu", pygame.Rect(WIDTH//2-100, 390, 200, 50))]
    sel = 0
    while True:
        screen.fill(theme["bg"])
        title = font.render("Paused", True, (0, 0, 200))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        for i, (txt, rect) in enumerate(btns): draw_button(rect, txt, active=(i == sel))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN): sel = 1 - sel
                elif event.key == pygame.K_RETURN: return btns[sel][0]
                elif event.key == pygame.K_r: return "Resume"

def end_game_screen(score, h_score):
    btns = [("Play Again", pygame.Rect(WIDTH//2-100, 320, 200, 50)), ("Return to Menu", pygame.Rect(WIDTH//2-100, 390, 200, 50))]
    sel = 0
    while True:
        screen.fill(theme["bg"])
        title = font.render("SNAKE(X) - You Lost", True, (200, 0, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        s_lbl = font.render(f"Your Score: {score}", True, theme["text"])
        screen.blit(s_lbl, (WIDTH//2 - s_lbl.get_width()//2, 180))
        h_lbl = font.render(f"High Score: {h_score}", True, theme["text"])
        screen.blit(h_lbl, (WIDTH//2 - h_lbl.get_width()//2, 230))
        for i, (txt, rect) in enumerate(btns): draw_button(rect, txt, active=(i == sel))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN): sel = 1 - sel
                elif event.key == pygame.K_RETURN: return btns[sel][0]

def play_game(session):
    global FPS, WIDTH, HEIGHT, screen, font, theme
    if session.paused_at > 0:
        session.total_paused_time += (pygame.time.get_ticks() - session.paused_at); session.paused_at = 0
    h_score = load_high_score() if session.mode != "Survival" else 0
    snake, direction, food_pos, score = session.snake, session.direction, session.food_position, session.score
    snake2, direction2, score2 = session.snake2, session.direction2, session.score2
    start_ticks, last_m, p_list = session.start_ticks, session.last_milestone, session.particles
    b_pos, b_life = session.bomb_position, session.bomb_lifetime
    running = True

    while running:
        n_head2 = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, SNAKE_SIZE): direction = (0, -SNAKE_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -SNAKE_SIZE): direction = (0, SNAKE_SIZE)
                elif event.key == pygame.K_LEFT and direction != (SNAKE_SIZE, 0): direction = (-SNAKE_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-SNAKE_SIZE, 0): direction = (SNAKE_SIZE, 0)
                if session.is_multiplayer:
                    if event.key == pygame.K_w and direction2 != (0, SNAKE_SIZE): direction2 = (0, -SNAKE_SIZE)
                    elif event.key == pygame.K_s and direction2 != (0, -SNAKE_SIZE): direction2 = (0, SNAKE_SIZE)
                    elif event.key == pygame.K_a and direction2 != (SNAKE_SIZE, 0): direction2 = (-SNAKE_SIZE, 0)
                    elif event.key == pygame.K_d and direction2 != (-SNAKE_SIZE, 0): direction2 = (SNAKE_SIZE, 0)
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    p_start = pygame.time.get_ticks()
                    res = pause_screen()
                    session.total_paused_time += (pygame.time.get_ticks() - p_start)
                    if res == "Return to Menu":
                        session.paused_at = pygame.time.get_ticks(); return None

        if session.mode == "Survival":
            if b_pos is None or b_life <= 0 or b_pos == food_pos or b_pos in snake:
                b_pos = get_new_bomb_position(snake, food_pos, session.obstacles); b_life = random.randint(80, 160)
            else: b_life -= 1

        n_head = ((snake[0][0] + direction[0]) % WIDTH, (snake[0][1] + direction[1]) % HEIGHT)
        if session.is_multiplayer: n_head2 = ((snake2[0][0] + direction2[0]) % WIDTH, (snake2[0][1] + direction2[1]) % HEIGHT)

        # Collisions
        if n_head in session.obstacles or (session.is_multiplayer and n_head2 in session.obstacles):
            play_sound('gameover'); particle_crash_effect(snake if n_head in session.obstacles else snake2, session=session)
            if session.mode == "Survival":
                game_over_name_entry(score, (pygame.time.get_ticks() - start_ticks - session.total_paused_time)//1000)
                return None
            if score > h_score: save_high_score(score)
            if end_game_screen(score, h_score if not session.is_multiplayer else score2) == "Play Again":
                new_session = GameSession(session.mode); play_game(new_session)
            return None

        if session.mode == "Survival" and is_on_bomb(n_head, b_pos):
            for _ in range(40): p_list.append(create_particle(b_pos[0]+16, b_pos[1]+16, (255, 60, 0)))
            for _ in range(20):
                temp = pygame.Surface((WIDTH, HEIGHT)); temp.fill(theme["bg"]); draw_grid(session.obstacles, temp)
                draw_snake(snake, 1, surface=temp); draw_food(food_pos, surface=temp); draw_bomb(b_pos, temp)
                for p in p_list[:]:
                    if p["life"] > 0:
                        p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1; pygame.draw.circle(temp, p["color"], (int(p["x"]), int(p["y"])), 4)
                    else: p_list.remove(p)
                screen.fill((0, 0, 0)); screen.blit(temp, (random.randint(-8, 8), random.randint(-8, 8))); pygame.display.flip()
                beep(1200, 40); pygame.time.delay(30)
            game_over_name_entry(score, (pygame.time.get_ticks() - start_ticks - session.total_paused_time)//1000); return None

        if n_head in snake or (session.is_multiplayer and (n_head in snake2 or n_head2 in snake2 or n_head2 in snake)):
            play_sound('gameover'); particle_crash_effect(snake if n_head in snake or (session.is_multiplayer and n_head in snake2) else snake2, session=session)
            if session.mode == "Survival":
                game_over_name_entry(score, (pygame.time.get_ticks() - start_ticks - session.total_paused_time)//1000); return None
            if score > h_score: save_high_score(score)
            if end_game_screen(score, h_score if not session.is_multiplayer else score2) == "Play Again":
                new_session = GameSession(session.mode); play_game(new_session)
            return None

        snake.insert(0, n_head)
        if session.is_multiplayer: snake2.insert(0, n_head2)

        ate1, ate2 = is_on_apple(snake[0], food_pos), session.is_multiplayer and is_on_apple(snake2[0], food_pos)
        if ate1 or ate2:
            now = pygame.time.get_ticks()
            session.multiplier = min(session.multiplier + 1, 5) if now - session.last_eat_time < 3000 else 1
            session.last_eat_time = now; score += 10 * session.multiplier if ate1 else 0; score2 += 10 * session.multiplier if ate2 else 0
            food_pos = get_new_food_position(snake + (snake2 if snake2 else []), session.obstacles); play_sound('eat')
            for _ in range(15): p_list.append(create_particle(food_pos[0], food_pos[1], theme["food"]))
        else:
            snake.pop()
            if session.is_multiplayer: snake2.pop()

        screen.fill(theme["bg"]); draw_grid(session.obstacles); draw_snake(snake, 1, session.multiplier)
        if session.is_multiplayer: draw_snake(snake2, 2, session.multiplier)
        draw_food(food_pos, math.sin(pygame.time.get_ticks()/200)*4)
        if session.mode == "Survival" and b_pos: draw_bomb(b_pos)

        screen.blit(font.render(f"P1: {score}", True, theme["text"]), (10, 10))
        if session.is_multiplayer: screen.blit(font.render(f"P2: {score2}", True, (100, 255, 255)), (10, 40))
        if session.multiplier > 1: screen.blit(font.render(f"x{session.multiplier}", True, (255, 255, 0)), (10, 70))

        elapsed = (pygame.time.get_ticks() - start_ticks - session.total_paused_time)//1000
        if session.mode == "Speed Run":
            rem = (session.game_duration - (pygame.time.get_ticks() - start_ticks - session.total_paused_time))//1000
            if rem <= 0: end_game_screen(score, h_score); return None
            screen.blit(font.render(f"Time: {rem}s", True, (255, 100, 100)), (WIDTH - 150, 10))
        else: screen.blit(font.render(f"Time: {elapsed//60:02}:{elapsed%60:02}", True, theme["text"]), (WIDTH - 150, 10))

        if score > 0 and score % 100 == 0 and score != last_m:
            score_pixel_animation(score, (110, 30), p_list); last_m = score

        for p in p_list[:]:
            if p["life"] > 0:
                pygame.draw.rect(screen, p["color"], (int(p["x"]), int(p["y"]), 5, 5))
                p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1
            else: p_list.remove(p)

        session.snake, session.direction, session.score, session.snake2, session.direction2, session.score2 = snake, direction, score, snake2, direction2, score2
        session.food_position, session.bomb_position, session.bomb_lifetime, session.last_milestone = food_pos, b_pos, b_life, last_m
        pygame.display.flip(); clock.tick(FPS)
    return None

def main():
    session = None
    while True:
        c = home_screen()
        if c == "Play New Game": session = GameSession("Normal"); play_game(session)
        elif c == "Multiplayer": session = GameSession("Multiplayer"); play_game(session)
        elif c == "Resume":
            if not session: session = GameSession("Normal")
            play_game(session)
        elif c == "Challenges":
            btns = [("Survival Mode", pygame.Rect(WIDTH//2-120, 180, 240, 60)), ("Walls of Doom", pygame.Rect(WIDTH//2-120, 260, 240, 60)), ("Speed Run", pygame.Rect(WIDTH//2-120, 340, 240, 60)), ("Back", pygame.Rect(WIDTH//2-120, 420, 240, 60))]
            sel = 0
            while True:
                screen.fill(theme["bg"])
                for i, (txt, rect) in enumerate(btns): draw_button(rect, txt, active=(i == sel))
                pygame.display.flip()
                ev = pygame.event.wait()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_UP: sel = (sel - 1) % len(btns)
                    elif ev.key == pygame.K_DOWN: sel = (sel + 1) % len(btns)
                    elif ev.key == pygame.K_RETURN:
                        if btns[sel][0] == "Back": break
                        session = GameSession(btns[sel][0].split()[0]); play_game(session); break
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    for i, (_, rect) in enumerate(btns):
                        if rect.collidepoint(ev.pos):
                            if btns[i][0] == "Back": break
                            session = GameSession(btns[i][0].split()[0]); play_game(session); break
                    break
        elif c == "Settings": settings_screen()
        elif c == "Quit": pygame.quit(); sys.exit()
        elif c == "Leaderboard":
            leaderboard = load_leaderboard()
            screen.fill(theme["bg"])
            y = 120
            for i, e in enumerate(leaderboard):
                screen.blit(font.render(f"{i+1}. {e['name']} - {e['score']} ({e['time']}s)", True, theme["text"]), (WIDTH//2-150, y)); y += 40
            pygame.display.flip(); pygame.event.wait()

if __name__ == "__main__":
    main()
