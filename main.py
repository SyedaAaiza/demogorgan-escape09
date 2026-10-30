import math
import os
import random
import sys
import json
import pygame
from UI.pause import PauseMenu
from obstacle import ObstacleManager

# --- CHARACTER SELECTION ROUTING ---
from movement.will_move import PlayerRunner as WillRunner

try:
    from movement.Mike_movement import PlayerRunner as MikeRunner
except ImportError:
    MikeRunner = WillRunner

try:
    from movement.eleven_movement import PlayerRunner as ElevenRunner
except ImportError:
    ElevenRunner = WillRunner

try:
    from movement.dustin_movement import PlayerRunner as DustinRunner
except ImportError:
    DustinRunner = WillRunner

try:
    from movement.lucas_movement import PlayerRunner as LucasRunner
except ImportError:
    LucasRunner = WillRunner

try:
    from movement.Max_movement import PlayerRunner as MaxRunner
except ImportError:
    MaxRunner = WillRunner

CHARACTER_CLASSES = {
    "WILL": WillRunner,
    "MIKE": MikeRunner,
    "ELEVEN": ElevenRunner,
    "DUSTIN": DustinRunner,
    "LUCAS": LucasRunner,
    "MAX": MaxRunner,
}


def run(volume=5, muted=False, selected_character=None):
    pygame.init()
    pygame.mixer.init()

    # Agar parameter na mile toh JSON file se character uthayega
    if selected_character is None:
        try:
            json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UI", "player_data.json")
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                    selected_character = data.get("selected_character", "WILL")
        except Exception as e:
            print(f"Error reading player_data.json: {e}")
            selected_character = "WILL"

    if not selected_character:
        selected_character = "WILL"

    actual_volume = 0.0 if muted else (volume / 10.0)

    DISP_WIDTH, DISP_HEIGHT = 1280, 720
    screen = pygame.display.set_mode((DISP_WIDTH, DISP_HEIGHT))
    pygame.display.set_caption(f"Stranger Things - Runner ({selected_character})")
    clock = pygame.time.Clock()

    WIDTH, HEIGHT = 800, 600
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    BG_PATH = os.path.join(ASSETS_DIR, "BG2.jpeg")

    try:
        background = pygame.image.load(BG_PATH).convert()
        background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))
    except pygame.error:
        print(f"Error: Could not load background at {BG_PATH}")
        sys.exit()

    for s2_ext in [".mp3", ".mpeg", ".ogg"]:
        s2_path = os.path.join(ASSETS_DIR, f"S2{s2_ext}")
        if os.path.exists(s2_path):
            try:
                pygame.mixer.music.load(s2_path)
                pygame.mixer.music.set_volume(actual_volume)
                pygame.mixer.music.play(-1)
                break
            except Exception as e:
                print(f"Could not play music {s2_path}: {e}")

    speed_factor = 1.0
    DIFFICULTY_RATE = 0.008

    # Yahan selected character ke mutabiq class load ho rahi hai
    char_class = CHARACTER_CLASSES.get(str(selected_character).upper(), WillRunner)
    print(f"Game successfully started with character: {str(selected_character).upper()}")
    player_runner = char_class(WIDTH, HEIGHT)

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

    font_title = pygame.font.SysFont(None, 72)
    font_gameover = pygame.font.SysFont(None, 45)
    font_hud = pygame.font.SysFont("Impact", 24)

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
            speed_factor += DIFFICULTY_RATE * (dt / 1000.0)

            screen_lanes = []
            horizon_y_screen = 0
            for ratio in LANE_RATIOS:
                top_x_screen = int(ratio["top_x"] * WIDTH)
                bottom_x_screen = int(ratio["bottom_x"] * WIDTH)
                top_y_screen = int(ratio["top_y"] * HEIGHT)
                screen_lanes.append({"top_x": top_x_screen, "bottom_x": bottom_x_screen})
                horizon_y_screen = top_y_screen

            obstacle_manager.lane_positions = screen_lanes
            obstacle_manager.HORIZON_Y = horizon_y_screen

            if hasattr(player_runner, "lane_positions"):
                player_runner.lane_positions = screen_lanes

            obstacle_manager.update_and_spawn(dt * speed_factor)
            player_runner.update(events)

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

            player_rect = (
                player_runner.get_rect()
                if hasattr(player_runner, "get_rect")
                else pygame.Rect(player_runner.x, player_runner.y, 130, 130)
            )

            game_surface.blit(background, (0, 0))
            obstacle_manager.draw(game_surface)

            for coin in coins_list:
                if coin["progress"] < 0:
                    continue
                lane_idx = coin["lane"]
                prog = coin["progress"]
                lane_data = screen_lanes[lane_idx]

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

            player_runner.draw(game_surface)

            if obstacle_manager.check_collision(player_runner):
                game_over = True
                frozen_snapshot = game_surface.copy()
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()

            pygame.draw.circle(game_surface, (255, 215, 0), (25, 25), 14)
            pygame.draw.circle(game_surface, (180, 130, 0), (25, 25), 14, 2)
            coin_label = font_hud.render(f"x {coins_collected}", True, (255, 255, 255))
            game_surface.blit(coin_label, (45, 15))

            pygame.draw.rect(game_surface, (30, 30, 45), pause_button_rect, border_radius=6)
            pygame.draw.rect(game_surface, (200, 50, 50), pause_button_rect, 2, border_radius=6)
            game_surface.blit(font_hud.render("||", True, (255, 255, 255)), (pause_button_rect.x + 11, pause_button_rect.y + 7))

        else:
            if frozen_snapshot:
                game_surface.blit(frozen_snapshot, (0, 0))

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((150, 0, 0, 140))
            game_surface.blit(overlay, (0, 0))

            text = font_gameover.render("HIT DETECTED! - Press R to Restart", True, (255, 255, 255))
            text_shadow = font_gameover.render("HIT DETECTED! - Press R to Restart", True, (0, 0, 0))

            game_surface.blit(text_shadow, (WIDTH // 2 - text.get_width() // 2 + 2, HEIGHT // 2 - 20 + 2))
            game_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))

        scaled_display = pygame.transform.smoothscale(game_surface, (DISP_WIDTH, DISP_HEIGHT))
        screen.blit(scaled_display, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()