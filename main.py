import os
import sys
import random
import math
import pygame
from obstacle import ObstacleManager
from movement.will_move import PlayerRunner
from UI.pause import PauseMenu


def draw_battery(surface, x, y, current_lives, max_l=5):
    bat_w, bat_h = 70, 22
    tip_w, tip_h = 4, 10

    bat_rect = pygame.Rect(x, y, bat_w, bat_h)
    tip_rect = pygame.Rect(x + bat_w, y + (bat_h - tip_h) // 2, tip_w, tip_h)

    pygame.draw.rect(surface, (220, 220, 220), bat_rect, 2, border_radius=4)
    pygame.draw.rect(surface, (220, 220, 220), tip_rect, border_radius=2)

    seg_margin = 3
    total_inner_w = bat_w - (seg_margin * (max_l + 1))
    seg_w = total_inner_w // max_l
    seg_h = bat_h - (seg_margin * 2)

    for i in range(max_l):
        seg_x = x + seg_margin + i * (seg_w + seg_margin)
        seg_y = y + seg_margin
        seg_rect = pygame.Rect(seg_x, seg_y, seg_w, seg_h)

        if i < current_lives:
            color = (50, 230, 50) if current_lives > 2 else (230, 50, 50)
        else:
            color = (40, 40, 50)

        pygame.draw.rect(surface, color, seg_rect, border_radius=2)


def run(volume=5, muted=False):
    pygame.init()
    pygame.mixer.init()

    # Calculate actual volume float (0.0 to 1.0)
    actual_volume = 0.0 if muted else (volume / 10.0)

    DISP_WIDTH, DISP_HEIGHT = 1280, 720
    screen = pygame.display.set_mode((DISP_WIDTH, DISP_HEIGHT))
    pygame.display.set_caption("Stranger Things - Runner")
    clock = pygame.time.Clock()

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

    # --- BACKGROUND MUSIC SETUP (S2) ---
    for s2_ext in [".mp3", ".mpeg", ".ogg"]:
        s2_path = os.path.join(ASSETS_DIR, f"S2{s2_ext}")
        if os.path.exists(s2_path):
            try:
                pygame.mixer.music.load(s2_path)
                pygame.mixer.music.set_volume(actual_volume)
                pygame.mixer.music.play(-1)
                print(f"Successfully loaded background music with volume {actual_volume}: {s2_path}")
                break
            except Exception as e:
                print(f"Could not play music {s2_path}: {e}")

    zoom = 1.0
    BASE_ZOOM_SPEED = 0.0004535
    MAX_ZOOM = 1.735

    # --- CONTINUOUS DIFFICULTY SYSTEM ---
    speed_factor = 1.0  # Game starts at 1x speed
    DIFFICULTY_RATE = 0.008  # Speed increases over time

    # Dynamic Ground Speed Lines to enforce forward depth motion
    ground_lines = [0.1, 0.3, 0.5, 0.7, 0.9]

    player_runner = PlayerRunner(WIDTH, HEIGHT)
    obstacle_manager = ObstacleManager(WIDTH, HEIGHT)
    pause_menu = PauseMenu(WIDTH, HEIGHT)

    LANE_RATIOS = [
        {"top_x": 0.435, "bottom_x": 0.22, "top_y": 0.38},
        {"top_x": 0.498, "bottom_x": 0.475, "top_y": 0.38},
        {"top_x": 0.565, "bottom_x": 0.74, "top_y": 0.38},
    ]

    coins_collected = 0
    coins_list = []
    coin_spawn_timer = 0

    lives = 5
    max_lives = 5
    hit_invulnerability_timer = 0

    font_title = pygame.font.SysFont(None, 72)
    font_gameover = pygame.font.SysFont(None, 45)
    font_hud = pygame.font.SysFont("Impact", 24)

    # Countdown
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
    pause_button_rect = pygame.Rect(WIDTH - 55, 15, 40, 40)

    while running:
        dt = clock.tick(60)
        events = pygame.event.get()

        if hit_invulnerability_timer > 0:
            hit_invulnerability_timer -= dt

        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                logic_mx = int(mx * (WIDTH / DISP_WIDTH))
                logic_my = int(my * (HEIGHT / DISP_HEIGHT))

                if pause_button_rect.collidepoint((logic_mx, logic_my)) and not game_over:
                    paused = True

            if game_over and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_R):
                    game_over = False
                    paused = False
                    frozen_snapshot = None
                    obstacle_manager.obstacles.clear()
                    coins_list.clear()
                    coins_collected = 0
                    lives = 5
                    hit_invulnerability_timer = 0
                    zoom = 1.0
                    speed_factor = 1.0
                    try:
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(actual_volume)
                    except Exception as e:
                        print(f"Error resetting music: {e}")

        if paused:
            action = pause_menu.run(screen, coins_collected, clock, DISP_WIDTH, DISP_HEIGHT, game_surface)
            if action == "RESUME":
                paused = False
            elif action == "RESTART":
                game_over = False
                paused = False
                frozen_snapshot = None
                obstacle_manager.obstacles.clear()
                coins_list.clear()
                coins_collected = 0
                lives = 5
                hit_invulnerability_timer = 0
                zoom = 1.0
                speed_factor = 1.0
                try:
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(actual_volume)
                except Exception as e:
                    print(f"Error resetting music: {e}")
            elif action == "QUIT":
                pygame.quit()
                sys.exit()
            continue

        game_surface.fill((0, 0, 0))

        if not game_over:
            # --- CONTINUOUS DIFFICULTY UPDATE ---
            speed_factor += DIFFICULTY_RATE * (dt / 1000.0)

            zoom += (BASE_ZOOM_SPEED * speed_factor) * dt
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

            obstacle_manager.update_and_spawn(dt * speed_factor)
            player_runner.update(events)

            # --- COIN SPAWN & PERSPECTIVE MOVEMENT ---
            coin_spawn_timer += dt
            if coin_spawn_timer > (1400 / speed_factor):
                coin_spawn_timer = 0
                chosen_lane = random.randint(0, 2)
                for i in range(4):
                    coins_list.append({"lane": chosen_lane, "progress": -0.12 * i})

            for coin in coins_list[:]:
                coin["progress"] += dt * 0.0006 * speed_factor
                if coin["progress"] >= 1.0:
                    coins_list.remove(coin)

            if hasattr(player_runner, 'get_rect'):
                player_rect = player_runner.get_rect()
            elif hasattr(player_runner, 'rect'):
                player_rect = player_runner.rect
            else:
                px = getattr(player_runner, 'char_x', getattr(player_runner, 'x', WIDTH // 2))
                py = getattr(player_runner, 'y', getattr(player_runner, 'player_y', HEIGHT - 150))
                player_rect = pygame.Rect(px + 10, py + 10, 50, 90)

            # --- DRAW BACKGROUND ---
            game_surface.blit(zoomed_bg, (x, y))

            # --- FORWARD MOTION PERSPECTIVE LINES (GROUND MOTION CUES) ---
            for i in range(len(ground_lines)):
                ground_lines[i] += dt * 0.0005 * speed_factor
                if ground_lines[i] >= 1.0:
                    ground_lines[i] = 0.0

                prog_line = ground_lines[i] ** 2.2
                line_y = int(horizon_y_screen + (HEIGHT - horizon_y_screen) * prog_line)
                line_width = int(2 + 10 * prog_line)
                line_alpha = int(180 * prog_line)

                line_surf = pygame.Surface((WIDTH, line_width), pygame.SRCALPHA)
                line_surf.fill((255, 50, 50, line_alpha))
                game_surface.blit(line_surf, (0, line_y))

            obstacle_manager.draw(game_surface)

            # --- DRAW COINS WITH EXPONENTIAL PERSPECTIVE CURVE ---
            for coin in coins_list:
                if coin["progress"] < 0:
                    continue
                lane_idx = coin["lane"]
                prog = coin["progress"]
                lane_data = screen_lanes[lane_idx]

                # Exponential curve: prog ** 2.2 makes items accelerate into view
                prog_curved = prog ** 2.2
                cx = int(lane_data["top_x"] + (lane_data["bottom_x"] - lane_data["top_x"]) * prog_curved)
                cy = int(horizon_y_screen + (HEIGHT - horizon_y_screen) * prog_curved)
                c_radius = int(4 + 14 * prog_curved)

                pygame.draw.circle(game_surface, (255, 215, 0), (cx, cy), c_radius)
                pygame.draw.circle(game_surface, (180, 130, 0), (cx, cy), c_radius, 2)

                coin_rect = pygame.Rect(cx - c_radius, cy - c_radius, c_radius * 2, c_radius * 2)
                if player_rect.colliderect(coin_rect):
                    coins_collected += 1
                    coins_list.remove(coin)

            # --- DRAW PLAYER WITH RUNNING BOBBING EFFECT ---
            run_bounce = math.sin(pygame.time.get_ticks() * 0.015 * speed_factor) * 4

            if hit_invulnerability_timer <= 0 or (hit_invulnerability_timer // 10) % 2 == 0:
                if hasattr(player_runner, 'draw'):
                    # Temporarily offset Y for running bob effect
                    original_y = getattr(player_runner, 'y', None)
                    if original_y is not None:
                        player_runner.y += run_bounce
                        player_runner.draw(game_surface)
                        player_runner.y = original_y
                    else:
                        player_runner.draw(game_surface)

            # --- COLLISION CHECK WITH 5 LIVES ---
            if obstacle_manager.check_collision(player_rect) and hit_invulnerability_timer <= 0:
                lives -= 1
                hit_invulnerability_timer = 90
                obstacle_manager.obstacles.clear()
                if lives <= 0:
                    game_over = True
                    frozen_snapshot = game_surface.copy()
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()

            # --- HUD DISPLAY ---
            pygame.draw.circle(game_surface, (255, 215, 0), (25, 25), 14)
            pygame.draw.circle(game_surface, (180, 130, 0), (25, 25), 14, 2)
            coin_label = font_hud.render(f"x {coins_collected}", True, (255, 255, 255))
            game_surface.blit(coin_label, (45, 15))

            draw_battery(game_surface, WIDTH - 145, 23, lives, max_lives)

            pygame.draw.rect(game_surface, (30, 30, 45), pause_button_rect, border_radius=6)
            pygame.draw.rect(game_surface, (200, 50, 50), pause_button_rect, 2, border_radius=6)
            game_surface.blit(font_hud.render("||", True, (255, 255, 255)),
                              (pause_button_rect.x + 11, pause_button_rect.y + 7))

        else:
            if frozen_snapshot:
                game_surface.blit(frozen_snapshot, (0, 0))

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((120, 0, 0, 130))
            game_surface.blit(overlay, (0, 0))

            text = font_gameover.render("GAME OVER - Press R to Restart", True, (255, 255, 255))
            text_shadow = font_gameover.render("GAME OVER - Press R to Restart", True, (0, 0, 0))

            game_surface.blit(text_shadow, (WIDTH // 2 - text.get_width() // 2 + 2, HEIGHT // 2 - 20 + 2))
            game_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))

        scaled_display = pygame.transform.smoothscale(game_surface, (DISP_WIDTH, DISP_HEIGHT))
        screen.blit(scaled_display, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()