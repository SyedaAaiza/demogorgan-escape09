import os
import sys
import random
import pygame
from obstacle import ObstacleManager
from movement.will_move import PlayerRunner

pygame.init()
pygame.mixer.init()

# 1. Main Window Display Resolution (Poori Widescreen Screen)
DISP_WIDTH, DISP_HEIGHT = 1280, 720
screen = pygame.display.set_mode((DISP_WIDTH, DISP_HEIGHT))
pygame.display.set_caption("Stranger Things - Runner")
clock = pygame.time.Clock()

# 2. Internal Game Logic Resolution (Jis par PlayerRunner & ObstacleManager design hain: 800x600)
WIDTH, HEIGHT = 800, 600
game_surface = pygame.Surface((WIDTH, HEIGHT))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BG_PATH = os.path.join(ASSETS_DIR, "BG2.jpeg")

try:
    background = pygame.image.load(BG_PATH).convert()
    background = pygame.transform.smoothscale(background, (WIDTH * 2, HEIGHT * 2))
except pygame.error:
    print(f"Error: Could not load background at {BG_PATH}")
    sys.exit()

zoom = 1.0
ZOOM_SPEED = 0.0004535
MAX_ZOOM = 1.735

player_runner = PlayerRunner(WIDTH, HEIGHT)
obstacle_manager = ObstacleManager(WIDTH, HEIGHT)

# Lane ratios perfectly calibrated for 800x600 center perspective
LANE_RATIOS = [
    {"top_x": 0.435, "bottom_x": 0.22, "top_y": 0.38},
    {"top_x": 0.498, "bottom_x": 0.475, "top_y": 0.38},
    {"top_x": 0.565, "bottom_x": 0.74, "top_y": 0.38},
]

# --- COIN SYSTEM SETUP (Subway Surfers Style Trails) ---
coins_collected = 0
coins_list = []
coin_spawn_timer = 0

# Fonts (rendered on 800x600 surface)
font_title = pygame.font.SysFont(None, 72)
font_menu = pygame.font.SysFont(None, 36)
font_gameover = pygame.font.SysFont(None, 45)
font_hud = pygame.font.SysFont("Impact", 24)

# --- 3, 2, 1, START! COUNTDOWN ---
countdown_steps = ["3", "2", "1", "START!"]
for step in countdown_steps:
    start_ticks = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_ticks < 1000:
        game_surface.fill((0, 0, 0))
        game_surface.blit(background, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        game_surface.blit(overlay, (0, 0))

        count_surf = font_title.render(step, True, (255, 50, 50))
        count_rect = count_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        game_surface.blit(count_surf, count_rect)

        # Scale game surface to fit 1280x720 window
        scaled_display = pygame.transform.smoothscale(game_surface, (DISP_WIDTH, DISP_HEIGHT))
        screen.blit(scaled_display, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

running = True
paused = False
game_over = False
frozen_snapshot = None

# Pause Button Rect on 800x600 surface
pause_button_rect = pygame.Rect(WIDTH - 65, 15, 45, 40)

while running:
    dt = clock.tick(60)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Map window mouse coordinates to 800x600 logic coordinates
            mx, my = event.pos
            logic_mx = int(mx * (WIDTH / DISP_WIDTH))
            logic_my = int(my * (HEIGHT / DISP_HEIGHT))

            if pause_button_rect.collidepoint((logic_mx, logic_my)) and not game_over:
                paused = not paused

        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r or event.key == pygame.K_R:
                game_over = False
                paused = False
                frozen_snapshot = None
                obstacle_manager.obstacles.clear()
                coins_list.clear()
                coins_collected = 0
                zoom = 1.0

    # If paused
    if paused:
        game_surface.fill((0, 0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        game_surface.blit(overlay, (0, 0))

        pause_title = font_title.render("GAME PAUSED", True, (255, 255, 255))
        resume_text = font_menu.render("Press P to Resume", True, (200, 200, 200))
        game_surface.blit(pause_title, (WIDTH // 2 - pause_title.get_width() // 2, HEIGHT // 2 - 40))
        game_surface.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 20))

        scaled_display = pygame.transform.smoothscale(game_surface, (DISP_WIDTH, DISP_HEIGHT))
        screen.blit(scaled_display, (0, 0))
        pygame.display.flip()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = False
        continue

    game_surface.fill((0, 0, 0))

    if not game_over:
        zoom += ZOOM_SPEED * dt
        if zoom >= MAX_ZOOM:
            zoom = 1.0

        scaled_width = int(WIDTH * zoom)
        scaled_height = int(HEIGHT * zoom)
        zoomed_bg = pygame.transform.smoothscale(background, (scaled_width, scaled_height))
        x = (WIDTH - scaled_width) // 2
        y = int((HEIGHT - scaled_height) // 2 + (zoom - 1.0) * 300)

        screen_lanes = []
        horizon_y_screen = 0
        for ratio in LANE_RATIOS:
            top_x_screen = x + int(ratio["top_x"] * scaled_width)
            bottom_x_screen = x + int(ratio["bottom_x"] * scaled_width)
            top_y_screen = y + int(ratio["top_y"] * scaled_height)
            screen_lanes.append({"top_x": top_x_screen, "bottom_x": bottom_x_screen})
            horizon_y_screen = top_y_screen

        obstacle_manager.lane_positions = screen_lanes
        obstacle_manager.HORIZON_Y = horizon_y_screen

        if hasattr(player_runner, 'lane_positions'):
            player_runner.lane_positions = screen_lanes

        obstacle_manager.update_and_spawn(dt)
        player_runner.update(events)

        # --- CONTINUOUS COIN TRAILS SPAWN (Subway Surfers Style) ---
        coin_spawn_timer += dt
        if coin_spawn_timer > 1400:
            coin_spawn_timer = 0
            chosen_lane = random.randint(0, 2)
            # Spawn a sequence of 4 coins in the same lane
            for i in range(4):
                coins_list.append({"lane": chosen_lane, "progress": -0.12 * i})

        for coin in coins_list[:]:
            coin["progress"] += dt * 0.0008 * (zoom * 1.5)
            if coin["progress"] >= 1.0:
                coins_list.remove(coin)

        # --- NATURAL & ACCURATE PLAYER COLLISION RECT ---
        if hasattr(player_runner, 'get_rect'):
            player_rect = player_runner.get_rect()
        elif hasattr(player_runner, 'rect'):
            player_rect = player_runner.rect
        else:
            px = getattr(player_runner, 'char_x', getattr(player_runner, 'x', WIDTH // 2))
            py = getattr(player_runner, 'y', getattr(player_runner, 'player_y', HEIGHT - 150))
            player_rect = pygame.Rect(px + 10, py + 10, 50, 90)

        # --- DRAW ON GAME SURFACE (800x600) ---
        game_surface.blit(zoomed_bg, (x, y))
        obstacle_manager.draw(game_surface)

        # Draw Continuous Coins
        for coin in coins_list:
            if coin["progress"] < 0:
                continue
            lane_idx = coin["lane"]
            prog = coin["progress"]
            lane_data = screen_lanes[lane_idx]

            cx = int(lane_data["top_x"] + (lane_data["bottom_x"] - lane_data["top_x"]) * prog)
            cy = int(horizon_y_screen + (HEIGHT - horizon_y_screen) * prog)
            c_radius = int(5 + 10 * prog)

            pygame.draw.circle(game_surface, (255, 215, 0), (cx, cy), c_radius)
            pygame.draw.circle(game_surface, (180, 130, 0), (cx, cy), c_radius, 2)

            # Coin Collection Check
            coin_rect = pygame.Rect(cx - c_radius, cy - c_radius, c_radius * 2, c_radius * 2)
            if player_rect.colliderect(coin_rect):
                coins_collected += 1
                coins_list.remove(coin)

        player_runner.draw(game_surface)

        # --- COLLISION CHECK & HIT CAPTURE ---
        if obstacle_manager.check_collision(player_rect):
            game_over = True
            frozen_snapshot = game_surface.copy()

        # --- RENDER HUD (Score & Pause Button) ---
        pygame.draw.circle(game_surface, (255, 215, 0), (25, 25), 14)
        pygame.draw.circle(game_surface, (180, 130, 0), (25, 25), 14, 2)
        coin_label = font_hud.render(f"x {coins_collected}", True, (255, 255, 255))
        game_surface.blit(coin_label, (45, 15))

        # Pause Button ("II" Icon)
        pygame.draw.rect(game_surface, (30, 30, 45), pause_button_rect, border_radius=6)
        pygame.draw.rect(game_surface, (200, 50, 50), pause_button_rect, 2, border_radius=6)
        game_surface.blit(font_hud.render("||", True, (255, 255, 255)),
                          (pause_button_rect.x + 12, pause_button_rect.y + 8))

    else:
        # --- GAME OVER SCREEN (Frozen Snapshot) ---
        if frozen_snapshot:
            game_surface.blit(frozen_snapshot, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((120, 0, 0, 130))
        game_surface.blit(overlay, (0, 0))

        text = font_gameover.render("HIT! GAME OVER - Press R to Restart", True, (255, 255, 255))
        text_shadow = font_gameover.render("HIT! GAME OVER - Press R to Restart", True, (0, 0, 0))

        game_surface.blit(text_shadow, (WIDTH // 2 - text.get_width() // 2 + 2, HEIGHT // 2 - 20 + 2))
        game_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))
    # --- FINAL DISPLAY BLIT (Smoothscales 800x600 -> 1280x720 Window) ---
    scaled_display = pygame.transform.smoothscale(game_surface, (DISP_WIDTH, DISP_HEIGHT))
    screen.blit(scaled_display, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()