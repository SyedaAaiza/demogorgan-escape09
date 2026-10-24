import math
import sys
import pygame
import os
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# 16:9 Widescreen Laptop Resolution
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape the Upside Down - Main Menu")
clock = pygame.time.Clock()

# --- Robust Asset Path Resolution ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FILENAME = os.path.join(BASE_DIR, "assets", "trees.jpeg")
if not os.path.exists(IMAGE_FILENAME):
    IMAGE_FILENAME = os.path.join(BASE_DIR, "..", "assets", "trees.jpeg")

MUSIC_FILENAME = os.path.join(BASE_DIR, "assets", "music.mp3")
if not os.path.exists(MUSIC_FILENAME):
    MUSIC_FILENAME = os.path.join(BASE_DIR, "..", "assets", "music.mp3")

try:
    bg_original = pygame.image.load(IMAGE_FILENAME).convert()
except FileNotFoundError:
    print(f"Error: Could not find '{IMAGE_FILENAME}' in assets folder.")
    pygame.quit()
    sys.exit()

# Menu Options
options = ["START GAME", "CUSTOMIZATION", "SETTINGS", "EXIT"]
selected_option = 0

# Fonts
font_menu = pygame.font.Font(None, 36)
font_title = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 24)

# --- JSON Data Management (Inside 'UI' folder) ---
UI_FOLDER = os.path.join(BASE_DIR, "UI")
DATA_FILE = os.path.join(UI_FOLDER, "player_data.json")


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "player_name": "Player",
        "selected_character": "Will",
        "sound": True,
        "music": True,
        "dark_mode": True
    }


def save_data(data):
    os.makedirs(UI_FOLDER, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


player_data = load_data()


# --- Handle Background Music State ---
def update_music_state():
    if player_data["music"]:
        try:
            if not pygame.mixer.music.get_busy():
                if os.path.exists(MUSIC_FILENAME):
                    pygame.mixer.music.load(MUSIC_FILENAME)
                    pygame.mixer.music.play(-1)
                is_playing = True
            else:
                pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Music load warning: {e}")
    else:
        try:
            pygame.mixer.music.pause()
        except:
            pass


# Start initial music if enabled
update_music_state()

# --- Infinite Smooth Zoom Variables ---
zoom_progress = 0.0
speed = 0.0015


def draw_styled_button(surface, text, center_x, center_y, width, height, is_selected):
    """Draws an arcade-style graphic box with glowing borders for menu items."""
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (center_x, center_y)

    if is_selected:
        bg_color = (180, 10, 10, 210)
        border_color = (255, 60, 60)
        text_color = (255, 255, 255)
        border_width = 3
    else:
        bg_color = (15, 15, 25, 170)
        border_color = (80, 80, 100)
        text_color = (180, 180, 180)
        border_width = 2

    box_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    box_surface.fill(bg_color)
    surface.blit(box_surface, rect.topleft)
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=6)

    if is_selected:
        pygame.draw.circle(surface, border_color, (rect.left - 15, rect.centery), 6)
        pygame.draw.circle(surface, border_color, (rect.right + 15, rect.centery), 6)

    text_surface = font_menu.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)
    return rect


# --- Seamless Countdown & Game Launch (Same Window) ---
def start_countdown_and_game():
    countdown_steps = ["3", "2", "1", "START!"]
    global zoom_progress

    for step in countdown_steps:
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 1000:
            zoom_progress += speed
            if zoom_progress >= 1.0:
                zoom_progress = 0.0

            screen.fill((0, 0, 0))
            scale1 = 1.0 + zoom_progress
            w1, h1 = int(WIDTH * scale1), int(HEIGHT * scale1)
            surf1 = pygame.transform.smoothscale(bg_original, (w1, h1))
            alpha1 = int((1.0 - zoom_progress) * 255)
            surf1.set_alpha(alpha1)
            screen.blit(surf1, ((WIDTH - w1) // 2, (HEIGHT - h1) // 2))

            vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            vignette.fill((0, 0, 0, 120))
            screen.blit(vignette, (0, 0))

            # Big Countdown Text
            count_surf = font_title.render(step, True, (255, 50, 50))
            count_rect = count_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            screen.blit(count_surf, count_rect)

            info_surf = font_menu.render(
                f"Playing as {player_data['selected_character']} ({player_data['player_name']})", True, (240, 240, 240))
            screen.blit(info_surf, (WIDTH // 2 - info_surf.get_width() // 2, HEIGHT // 2 + 50))

            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    # --- SEAMLESS HANDOFF TO MAIN GAME (Same Window) ---
    try:
        import main
        if hasattr(main, 'run_game'):
            main.run_game(screen, player_data)
        else:
            print("Error: main.py mein 'run_game(screen, player_data)' function define hona chahiye.")
    except ImportError:
        print("Error: main.py file nahi mili!")


# --- Customization Screen (Imports separate code from UI folder) ---
def customization_screen():
    global player_data
    try:
        # Import your separate customization script from the UI folder
        from UI import customization as char_custom
        if hasattr(char_custom, 'run_customization'):
            player_data = char_custom.run_customization(screen, player_data)
            save_data(player_data)
            return
    except ImportError:
        print("Warning: 'UI/customization.py' module not found. Please create it or check path.")

    # Fallback backup UI if external module isn't loaded yet
    while True:
        screen.fill((15, 15, 25))
        title_surf = font_title.render("CUSTOMIZATION MODULE MISSING", True, (230, 20, 20))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 180))

        desc_surf = font_menu.render("Please place your customization script inside the UI folder.", True,
                                     (200, 200, 200))
        screen.blit(desc_surf, (WIDTH // 2 - desc_surf.get_width() // 2, 280))

        back_rect = pygame.Rect(WIDTH // 2 - 100, 420, 200, 50)
        pygame.draw.rect(screen, (40, 40, 60), back_rect, border_radius=6)
        pygame.draw.rect(screen, (230, 20, 20), back_rect, 2, border_radius=6)
        back_txt = font_menu.render("BACK", True, (255, 255, 255))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_rect.collidepoint(event.pos):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        pygame.display.flip()
        clock.tick(60)


# --- Settings Screen ---
def settings_screen():
    global player_data
    while True:
        screen.fill((15, 15, 25))
        title_surf = font_title.render("SETTINGS", True, (230, 20, 20))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 80))

        sound_txt = font_menu.render(f"Sound Effects: {'ON' if player_data['sound'] else 'OFF'}", True, (240, 240, 240))
        music_txt = font_menu.render(f"Background Music: {'ON' if player_data['music'] else 'OFF'}", True,
                                     (240, 240, 240))

        sound_rect = pygame.Rect(WIDTH // 2 - 200, 240, 400, 50)
        music_rect = pygame.Rect(WIDTH // 2 - 200, 310, 400, 50)

        pygame.draw.rect(screen, (30, 30, 45), sound_rect, border_radius=6)
        pygame.draw.rect(screen, (30, 30, 45), music_rect, border_radius=6)

        screen.blit(sound_txt, (sound_rect.x + 20, sound_rect.y + 12))
        screen.blit(music_txt, (music_rect.x + 20, music_rect.y + 12))

        back_rect = pygame.Rect(WIDTH // 2 - 100, 480, 200, 50)
        pygame.draw.rect(screen, (40, 40, 60), back_rect, border_radius=6)
        pygame.draw.rect(screen, (230, 20, 20), back_rect, 2, border_radius=6)
        back_txt = font_menu.render("BACK", True, (255, 255, 255))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_rect.collidepoint(event.pos):
                    player_data["sound"] = not player_data["sound"]
                elif music_rect.collidepoint(event.pos):
                    player_data["music"] = not player_data["music"]
                    update_music_state()
                elif back_rect.collidepoint(event.pos):
                    save_data(player_data)
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                save_data(player_data)
                return

        pygame.display.flip()
        clock.tick(60)


# --- Main Menu Loop ---
running = True
while running:
    zoom_progress += speed
    if zoom_progress >= 1.0:
        zoom_progress = 0.0

    screen.fill((0, 0, 0))

    # Dual-Layer Seamless Cross-Fade Logic
    scale1 = 1.0 + zoom_progress
    w1, h1 = int(WIDTH * scale1), int(HEIGHT * scale1)
    surf1 = pygame.transform.smoothscale(bg_original, (w1, h1))
    alpha1 = int((1.0 - zoom_progress) * 255)
    surf1.set_alpha(alpha1)
    screen.blit(surf1, ((WIDTH - w1) // 2, (HEIGHT - h1) // 2))

    scale2 = 1.0 + zoom_progress
    if zoom_progress < 0.5:
        scale2 = 1.0 + zoom_progress + 0.5
    else:
        scale2 = 1.0 + zoom_progress - 0.5

    w2, h2 = int(WIDTH * scale2), int(HEIGHT * scale2)
    surf2 = pygame.transform.smoothscale(bg_original, (w2, h2))
    alpha2 = 255 - alpha1
    surf2.set_alpha(max(0, min(255, alpha2)))
    screen.blit(surf2, ((WIDTH - w2) // 2, (HEIGHT - h2) // 2))

    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    vignette.fill((0, 0, 0, 80))
    screen.blit(vignette, (0, 0))

    # Title Display with Shadow
    title_surface = font_title.render("ESCAPE THE UPSIDE DOWN", True, (230, 20, 20))
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 110))
    shadow_surface = font_title.render("ESCAPE THE UPSIDE DOWN", True, (0, 0, 0))
    screen.blit(shadow_surface, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title_surface, title_rect)

    # Render Graphic Menu Buttons
    button_w, button_h = 320, 50
    start_y = 280
    spacing = 70
    button_rects = []

    for i, option in enumerate(options):
        y_pos = start_y + (i * spacing)
        is_selected = i == selected_option
        b_rect = draw_styled_button(screen, option, WIDTH // 2, y_pos, button_w, button_h, is_selected)
        button_rects.append(b_rect)

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                selected_option = (selected_option + 1) % len(options)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                selected_option = (selected_option - 1) % len(options)
            elif event.key == pygame.K_RETURN:
                choice = options[selected_option]
                if choice == "START GAME":
                    start_countdown_and_game()
                elif choice == "CUSTOMIZATION":
                    customization_screen()
                elif choice == "SETTINGS":
                    settings_screen()
                elif choice == "EXIT":
                    pygame.quit()
                    sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, b_rect in enumerate(button_rects):
                if b_rect.collidepoint(event.pos):
                    selected_option = i
                    choice = options[selected_option]
                    if choice == "START GAME":
                        start_countdown_and_game()
                    elif choice == "CUSTOMIZATION":
                        customization_screen()
                    elif choice == "SETTINGS":
                        settings_screen()
                    elif choice == "EXIT":
                        pygame.quit()
                        sys.exit()

    pygame.display.flip()
    clock.tick(60)