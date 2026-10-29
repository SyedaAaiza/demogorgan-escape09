import os
import random
import sys
import math
import pygame

from UI.pause import PauseMenu
from movement.will_move import PlayerRunner as WillRunner
from obstacle import ObstacleManager
from UI.game_over import AestheticHorrorGameOver

# --- CHARACTER SELECTION ROUTING ---
try:
    from movement.mike_move import PlayerRunner as MikeRunner
except ImportError:
    MikeRunner = WillRunner

try:
    from movement.eleven_move import PlayerRunner as ElevenRunner
except ImportError:
    ElevenRunner = WillRunner

try:
    from movement.dustin_move import PlayerRunner as DustinRunner
except ImportError:
    DustinRunner = WillRunner

try:
    from movement.lucas_move import PlayerRunner as LucasRunner
except ImportError:
    LucasRunner = WillRunner

CHARACTER_CLASSES = {
    "WILL": WillRunner,
    "MIKE": MikeRunner,
    "ELEVEN": ElevenRunner,
    "DUSTIN": DustinRunner,
    "LUCAS": LucasRunner,
}


def run(volume=5, muted=False, selected_character="WILL"):
    pygame.init()

    try:
        pygame.mixer.init()
    except pygame.error as e:
        print(f"Audio initialization failed: {e}")

    actual_volume = 0.0 if muted else max(0.0, min(1.0, volume / 10.0))

    DISP_WIDTH, DISP_HEIGHT = 1280, 720
    WIDTH, HEIGHT = 800, 600

    screen = pygame.display.set_mode((DISP_WIDTH, DISP_HEIGHT))
    pygame.display.set_caption("Stranger Things - Runner")

    clock = pygame.time.Clock()
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    track_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # --- UI ---
    game_over_ui = AestheticHorrorGameOver(WIDTH, HEIGHT)
    pause_menu = PauseMenu(WIDTH, HEIGHT)

    # --- ASSETS ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    BG_PATH = os.path.join(ASSETS_DIR, "BG2.jpeg")

    try:
        background = pygame.image.load(BG_PATH).convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except (pygame.error, OSError) as e:
        print(f"Error loading background: {BG_PATH}\n{e}")
        pygame.quit()
        return

    # --- COIN PNG ASSET LOADING ---
    coin_img_original = None
    COIN_PNG_PATH = os.path.join(ASSETS_DIR, "coin.png")

    if os.path.exists(COIN_PNG_PATH):
        try:
            coin_img_original = pygame.image.load(COIN_PNG_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Could not load coin image: {e}")

    # ==========================================================
    # BACKGROUND ZOOM & TRACK MOTION
    # ==========================================================
    ZOOM_CYCLE_SECONDS = 3.0
    MAX_ZOOM = 1.30
    CROSSFADE_START = 0.80

    background_start_ticks = pygame.time.get_ticks()
    track_offset = 0.0

    def draw_animated_background(surface, current_speed_factor):
        cycle_time = ZOOM_CYCLE_SECONDS / current_speed_factor
        elapsed = (pygame.time.get_ticks() - background_start_ticks) / 1000.0
        phase = (elapsed % cycle_time) / cycle_time

        zoom = 1.0 + (MAX_ZOOM - 1.0) * phase

        scaled_width = int(WIDTH * zoom)
        scaled_height = int(HEIGHT * zoom)

        scaled_bg = pygame.transform.smoothscale(background, (scaled_width, scaled_height))

        x = (WIDTH - scaled_width) // 2
        y = (HEIGHT - scaled_height) // 2

        surface.blit(scaled_bg, (x, y))

        if phase >= CROSSFADE_START:
            fade_progress = (phase - CROSSFADE_START) / (1.0 - CROSSFADE_START)
            fade_progress = fade_progress * fade_progress * (3.0 - 2.0 * fade_progress)

            fade_surface.fill((0, 0, 0, 0))
            fade_surface.blit(background, (0, 0))
            fade_surface.set_alpha(int(255 * fade_progress))

            surface.blit(fade_surface, (0, 0))

    def draw_track_motion(surface, dt, speed_factor, screen_lanes, horizon_y):
        nonlocal track_offset
        track_offset += dt * 0.0015 * speed_factor
        if track_offset >= 1.0:
            track_offset -= 1.0

        track_surface.fill((0, 0, 0, 0))

        for i in range(8):
            prog = (track_offset + (i * 0.125)) % 1.0
            prog_curved = prog ** 2.2

            y_pos = int(horizon_y + (HEIGHT - horizon_y) * prog_curved)
            alpha = int(180 * prog_curved)

            x_left = int(
                screen_lanes[0]["top_x"] + (screen_lanes[0]["bottom_x"] - screen_lanes[0]["top_x"]) * prog_curved)
            x_right = int(
                screen_lanes[2]["top_x"] + (screen_lanes[2]["bottom_x"] - screen_lanes[2]["top_x"]) * prog_curved)

            thickness = max(1, int(2 + 4 * prog_curved))

            pygame.draw.line(
                track_surface,
                (20, 15, 30, alpha),
                (x_left - 30, y_pos),
                (x_right + 30, y_pos),
                thickness
            )

        surface.blit(track_surface, (0, 0))

    # ==========================================================
    # BATTERY INDICATOR
    # ==========================================================
    MAX_LIVES = 5

    def draw_battery(surface, lives):
        battery_x = WIDTH - 100
        battery_y = 65
        battery_w = 84
        battery_h = 25

        pygame.draw.rect(
            surface,
            (220, 220, 220),
            (battery_x, battery_y, battery_w, battery_h),
            2,
            border_radius=4,
        )

        pygame.draw.rect(
            surface,
            (220, 220, 220),
            (battery_x + battery_w, battery_y + 7, 5, 11),
            border_radius=2,
        )

        padding = 4
        gap = 3

        segment_w = (battery_w - 2 * padding - 4 * gap) // MAX_LIVES
        segment_h = battery_h - 2 * padding

        for i in range(MAX_LIVES):
            segment_x = battery_x + padding + i * (segment_w + gap)
            segment_y = battery_y + padding

            color = (60, 230, 100) if i < lives else (75, 75, 75)

            pygame.draw.rect(
                surface,
                color,
                (segment_x, segment_y, segment_w, segment_h),
                border_radius=2,
            )

    # ==========================================================
    # HEART HEALTH INDICATOR
    # ==========================================================
    def draw_health_heart(surface, health):
        heart_x = WIDTH - 94
        heart_y = 100
        heart_w = 32
        heart_h = 30

        health = max(0, min(100, health))

        points = [
            (heart_w // 2, heart_h - 1),
            (2, 12),
            (2, 8),
            (5, 3),
            (10, 1),
            (heart_w // 2, 8),
            (heart_w - 10, 1),
            (heart_w - 5, 3),
            (heart_w - 2, 8),
            (heart_w - 2, 12),
        ]

        heart_surface = pygame.Surface((heart_w, heart_h), pygame.SRCALPHA)
        pygame.draw.polygon(heart_surface, (65, 25, 30), points)

        fill_height = int(heart_h * health / 100)

        if fill_height > 0:
            previous_clip = heart_surface.get_clip()
            heart_surface.set_clip(
                pygame.Rect(0, heart_h - fill_height, heart_w, fill_height)
            )
            pygame.draw.polygon(heart_surface, (235, 35, 55), points)
            heart_surface.set_clip(previous_clip)

        pygame.draw.polygon(heart_surface, (255, 205, 210), points, 2)
        surface.blit(heart_surface, (heart_x, heart_y))

        health_font = pygame.font.SysFont("Impact", 20)
        health_text = health_font.render(f"{health}%", True, (255, 255, 255))
        surface.blit(health_text, (heart_x + 38, heart_y + 4))

    # ==========================================================
    # MUSIC
    # ==========================================================
    if pygame.mixer.get_init():
        for extension in [".mp3", ".mpeg", ".ogg"]:
            music_path = os.path.join(ASSETS_DIR, f"S2{extension}")

            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(actual_volume)
                    pygame.mixer.music.play(-1)
                    break
                except pygame.error as e:
                    print(f"Could not play music: {e}")

    # ==========================================================
    # GAME INITIALIZATION
    # ==========================================================
    speed_factor = 1.0
    DIFFICULTY_RATE = 0.002
    MAX_SPEED_FACTOR = 2.2

    char_class = CHARACTER_CLASSES.get(selected_character.upper(), WillRunner)

    player_runner = char_class(WIDTH, HEIGHT)
    obstacle_manager = ObstacleManager(WIDTH, HEIGHT)

    LANE_RATIOS = [
        {"top_x": 0.435, "bottom_x": 0.16, "top_y": 0.38},  # Left
        {"top_x": 0.498, "bottom_x": 0.475, "top_y": 0.38},  # Center
        {"top_x": 0.565, "bottom_x": 0.80, "top_y": 0.38},  # Right
    ]

    coins_collected = 0
    coins_list = []
    coin_spawn_timer = 0

    # --- INITIAL COIN LAYOUT WITH ARC JUMP HEIGHT ---
    for lane in [0, 2]:
        for i in range(5):
            # i=0 -> 0, i=1 -> 40, i=2 -> 60, i=3 -> 40, i=4 -> 0 (Jump Arc Curve)
            arc_height = math.sin((i / 4.0) * math.pi) * 60
            coins_list.append({
                "lane": lane,
                "progress": 0.15 + (i * 0.12),
                "y_offset": arc_height
            })

    lives_remaining = MAX_LIVES
    health_percentage = 100
    collision_active = False

    font_title = pygame.font.SysFont(None, 72)
    font_hud = pygame.font.SysFont("Impact", 24)

    # ==========================================================
    # COUNTDOWN
    # ==========================================================
    countdown_steps = ["3", "2", "1", "START!"]

    for step in countdown_steps:
        start_ticks = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_ticks < 1000:
            game_surface.fill((0, 0, 0))
            draw_animated_background(game_surface, 1.0)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            game_surface.blit(overlay, (0, 0))

            count_surf = font_title.render(step, True, (255, 50, 50))
            count_rect = count_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            game_surface.blit(count_surf, count_rect)

            scaled_display = pygame.transform.scale(
                game_surface, (DISP_WIDTH, DISP_HEIGHT)
            )
            screen.blit(scaled_display, (0, 0))
            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    background_start_ticks = pygame.time.get_ticks()

    # ==========================================================
    # MAIN LOOP
    # ==========================================================
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

            # --- GAME OVER INPUT ---
            if game_over:
                event_copy = event
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    logic_mx = int(mx * (WIDTH / DISP_WIDTH))
                    logic_my = int(my * (HEIGHT / DISP_HEIGHT))

                    event_copy = pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN,
                        {"button": event.button, "pos": (logic_mx, logic_my)},
                    )

                action = game_over_ui.handle_input(event_copy)

                if action == "restart":
                    game_over = False
                    paused = False
                    frozen_snapshot = None

                    obstacle_manager.obstacles.clear()
                    coins_list.clear()

                    for lane in [0, 2]:
                        for i in range(5):
                            arc_height = math.sin((i / 4.0) * math.pi) * 60
                            coins_list.append({
                                "lane": lane,
                                "progress": 0.15 + (i * 0.12),
                                "y_offset": arc_height
                            })

                    coins_collected = 0
                    coin_spawn_timer = 0
                    speed_factor = 1.0

                    lives_remaining = MAX_LIVES
                    health_percentage = 100
                    collision_active = False

                    background_start_ticks = pygame.time.get_ticks()

                    if pygame.mixer.get_init():
                        try:
                            pygame.mixer.music.play(-1)
                            pygame.mixer.music.set_volume(actual_volume)
                        except pygame.error as e:
                            print(f"Error resetting music: {e}")

                elif action == "menu":
                    running = False

                elif action == "quit":
                    pygame.quit()
                    sys.exit()

        # ======================================================
        # PAUSE MENU
        # ======================================================
        if paused:
            action = pause_menu.run(
                screen,
                coins_collected,
                clock,
                DISP_WIDTH,
                DISP_HEIGHT,
                game_surface,
            )

            if action == "RESUME":
                paused = False

            elif action == "RESTART":
                game_over = False
                paused = False
                frozen_snapshot = None

                obstacle_manager.obstacles.clear()
                coins_list.clear()

                for lane in [0, 2]:
                    for i in range(5):
                        arc_height = math.sin((i / 4.0) * math.pi) * 60
                        coins_list.append({
                            "lane": lane,
                            "progress": 0.15 + (i * 0.12),
                            "y_offset": arc_height
                        })

                coins_collected = 0
                coin_spawn_timer = 0
                speed_factor = 1.0

                lives_remaining = MAX_LIVES
                health_percentage = 100
                collision_active = False

                background_start_ticks = pygame.time.get_ticks()

                if pygame.mixer.get_init():
                    try:
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(actual_volume)
                    except pygame.error as e:
                        print(f"Error resetting music: {e}")

            elif action == "QUIT":
                pygame.quit()
                sys.exit()

            continue

        game_surface.fill((0, 0, 0))

        # ======================================================
        # ACTIVE GAMEPLAY
        # ======================================================
        if not game_over:
            speed_factor = min(
                MAX_SPEED_FACTOR, speed_factor + DIFFICULTY_RATE * (dt / 1000.0)
            )

            screen_lanes = []
            horizon_y_screen = 0

            for ratio in LANE_RATIOS:
                top_x_screen = int(ratio["top_x"] * WIDTH)
                bottom_x_screen = int(ratio["bottom_x"] * WIDTH)
                top_y_screen = int(ratio["top_y"] * HEIGHT)

                screen_lanes.append(
                    {"top_x": top_x_screen, "bottom_x": bottom_x_screen}
                )
                horizon_y_screen = top_y_screen

            obstacle_manager.lane_positions = screen_lanes
            obstacle_manager.HORIZON_Y = horizon_y_screen

            if hasattr(player_runner, "lane_positions"):
                player_runner.lane_positions = screen_lanes

            obstacle_manager.update_and_spawn(dt * speed_factor)
            player_runner.update(events)

            # --- COIN SPAWNING WITH ARC JUMP SHAPE ---
            coin_spawn_timer += dt

            if coin_spawn_timer > (550 / speed_factor):
                coin_spawn_timer = 0
                chosen_lanes = random.sample([0, 1, 2], k=2)

                for lane in chosen_lanes:
                    is_arc_jump = random.choice([True, False])
                    for i in range(5):
                        # अगर Arc जंप है तो सिनसॉइडल कर्व बनेगा (ऑब्स्टैकल के ऊपर से कूदने का शेप)
                        y_arc = (math.sin((i / 4.0) * math.pi) * 75) if is_arc_jump else 0.0
                        coins_list.append({
                            "lane": lane,
                            "progress": 0.0 + (i * 0.09),
                            "y_offset": y_arc
                        })

            # --- COIN MOVEMENT ---
            for coin in coins_list[:]:
                coin["progress"] += dt * 0.0006 * speed_factor

                if coin["progress"] >= 1.0:
                    coins_list.remove(coin)

            player_rect = (
                player_runner.get_rect()
                if hasattr(player_runner, "get_rect")
                else pygame.Rect(player_runner.x, player_runner.y, 130, 130)
            )

            # --- BACKGROUND & TRACK LINES ---
            draw_animated_background(game_surface, speed_factor)
            draw_track_motion(game_surface, dt, speed_factor, screen_lanes, horizon_y_screen)

            # --- OBSTACLES ---
            obstacle_manager.draw(game_surface)

            # --- COINS AND DRAWING ---
            for coin in coins_list[:]:
                if coin["progress"] < 0:
                    continue

                lane_idx = coin["lane"]
                prog = coin["progress"]
                lane_data = screen_lanes[lane_idx]

                prog_curved = prog ** 2.0

                cx = int(
                    lane_data["top_x"]
                    + (lane_data["bottom_x"] - lane_data["top_x"]) * prog_curved
                )

                # Z-perspective Y position
                base_cy = horizon_y_screen + (HEIGHT - horizon_y_screen) * prog_curved

                # Arc curve applies extra Y lift as coins get closer to the camera
                cy = int(base_cy - (coin.get("y_offset", 0.0) * prog_curved))

                c_radius = int(14 + 22 * prog_curved)
                coin_size = max(1, c_radius * 2)

                if coin_img_original:
                    scaled_coin = pygame.transform.smoothscale(
                        coin_img_original, (coin_size, coin_size)
                    )
                    game_surface.blit(scaled_coin, (cx - c_radius, cy - c_radius))
                else:
                    pygame.draw.circle(game_surface, (255, 215, 0), (cx, cy), c_radius)
                    pygame.draw.circle(
                        game_surface, (180, 130, 0), (cx, cy), c_radius, 2
                    )

                coin_rect = pygame.Rect(
                    cx - c_radius, cy - c_radius, coin_size, coin_size
                )

                # ======================================================
                # EASY & INSTANT COIN COLLECTION (ACCURATE COLLISION)
                # ======================================================
                if player_rect.colliderect(coin_rect):
                    coins_collected += 1
                    coins_list.remove(coin)

            # --- PLAYER DRAWING ---
            player_runner.draw(game_surface)

            # ==================================================
            # COLLISION, LIVES AND HEALTH
            # ==================================================
            collision_now = obstacle_manager.check_collision(player_runner)

            if collision_now and not collision_active:
                lives_remaining = max(0, lives_remaining - 1)
                health_percentage = int((lives_remaining / MAX_LIVES) * 100)
                collision_active = True

                if lives_remaining == 0:
                    game_over = True
                    frozen_snapshot = game_surface.copy()

                    if pygame.mixer.get_init():
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()

            elif not collision_now:
                collision_active = False

            # --- COIN COUNTER ---
            if coin_img_original:
                hud_coin = pygame.transform.smoothscale(coin_img_original, (32, 32))
                game_surface.blit(hud_coin, (10, 10))
            else:
                pygame.draw.circle(game_surface, (255, 215, 0), (25, 25), 14)
                pygame.draw.circle(game_surface, (180, 130, 0), (25, 25), 14, 2)

            coin_label = font_hud.render(
                f"x {coins_collected}", True, (255, 255, 255)
            )
            game_surface.blit(coin_label, (48, 15))

            # --- PAUSE BUTTON ---
            pygame.draw.rect(
                game_surface, (30, 30, 45), pause_button_rect, border_radius=6
            )
            pygame.draw.rect(
                game_surface,
                (200, 50, 50),
                pause_button_rect,
                2,
                border_radius=6,
            )

            game_surface.blit(
                font_hud.render("||", True, (255, 255, 255)),
                (pause_button_rect.x + 11, pause_button_rect.y + 7),
            )

            # --- BATTERY & HEART INDICATORS ---
            draw_battery(game_surface, lives_remaining)
            draw_health_heart(game_surface, health_percentage)

        # ======================================================
        # GAME OVER
        # ======================================================
        else:
            if frozen_snapshot is not None:
                game_surface.blit(frozen_snapshot, (0, 0))

            game_over_ui.draw(
                game_surface,
                final_score=coins_collected,
                max_lives=MAX_LIVES,
            )

        # --- SCALE AND DISPLAY ---
        scaled_display = pygame.transform.scale(
            game_surface, (DISP_WIDTH, DISP_HEIGHT)
        )

        screen.blit(scaled_display, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()