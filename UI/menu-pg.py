import math
import sys
import os
import json
import subprocess
import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# 16:9 Widescreen Laptop Resolution
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape the Upside Down - Main Menu")
clock = pygame.time.Clock()

# --- INITIALIZATION & ASSETS ---
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

# --- JSON DATA MANAGEMENT ---
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


# --- BACKGROUND MUSIC HANDLER ---
def update_music_state():
    if player_data["music"]:
        try:
            if not pygame.mixer.music.get_busy():
                if os.path.exists(MUSIC_FILENAME):
                    pygame.mixer.music.load(MUSIC_FILENAME)
                    pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Music load warning: {e}")
    else:
        try:
            pygame.mixer.music.pause()
        except:
            pass


update_music_state()

# Infinite Smooth Zoom Variables
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


# ==============================================================================
# **START GAME BUTTON CODE (Thunder Warning + Seamless Game Handoff)**
# ==============================================================================
def start_game_action():
    """Shows an atmospheric Upside Down warning screen with lightning effects and thunder sound, then launches main.py."""
    global zoom_progress

    # Load thunder sound if available in assets
    thunder_path = os.path.join(BASE_DIR, "assets", "thunder.mp3")
    if not os.path.exists(thunder_path):
        thunder_path = os.path.join(BASE_DIR, "..", "assets", "thunder.mp3")

    thunder_sound = None
    try:
        if os.path.exists(thunder_path):
            thunder_sound = pygame.mixer.Sound(thunder_path)
    except Exception as e:
        print(f"Thunder sound load warning: {e}")

    warning_active = True
    flash_timer = 0
    flash_alpha = 0

    # Stylized warning fonts
    try:
        font_warning_title = pygame.font.SysFont("Impact", 60)
        font_warning_body = pygame.font.SysFont("Courier New", 24, bold=True)
    except:
        font_warning_title = font_title
        font_warning_body = font_menu

    while warning_active:
        # Lightning flash animation trigger
        flash_timer += 1
        if flash_timer % 110 == 0:  # Flash periodically
            flash_alpha = 200
            if thunder_sound and player_data["sound"]:
                thunder_sound.play()

        if flash_alpha > 0:
            flash_alpha -= 12  # Fade out flash quickly

        # Background color reacts to lightning flash
        bg_r = min(255, 10 + flash_alpha)
        bg_g = min(255, 0 + int(flash_alpha * 0.15))
        bg_b = min(255, 0 + int(flash_alpha * 0.15))
        screen.fill((bg_r, bg_g, bg_b))

        # Spooky vignette overlay
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        vignette.fill((15, 0, 0, 230))
        screen.blit(vignette, (0, 0))

        # Warning Text Styling with Shadow
        title_surf = font_warning_title.render("WARNING: ENTERING THE RIFT", True, (255, 40, 40))
        title_shadow = font_warning_title.render("WARNING: ENTERING THE RIFT", True, (40, 0, 0))

        text1 = font_warning_body.render("You are crossing into the unstable Upside Down dimension.", True,
                                         (220, 220, 220))
        text2 = font_warning_body.render("Demogorgons and shadow entities are waiting in the dark...", True,
                                         (200, 100, 100))
        prompt = font_small.render("[ PRESS ENTER OR CLICK TO ENTER ]", True, (255, 255, 255))

        t_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110))
        s_rect = title_shadow.get_rect(center=(WIDTH // 2 - 2, HEIGHT // 2 - 108))

        screen.blit(title_shadow, s_rect)
        screen.blit(title_surf, t_rect)

        screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 20))
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 20))

        # Blinking prompt effect
        if (pygame.time.get_ticks() // 400) % 2 == 0:
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 110))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    warning_active = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                warning_active = False

    # --- HANDOFF TO MAIN GAME (`main.py`) ---
    try:
        import main
        if hasattr(main, 'run_game'):
            # Opens main.py in the exact same fullscreen/window resolution
            main.run_game(screen, player_data)
        else:
            print("Error: main.py mein 'run_game(screen, player_data)' function define hona chahiye.")
    except ImportError:
        print("Error: main.py file nahi mili root directory mein!")


# ==========================================
# **CUSTOMIZATION SCREEN CODE**
# ==========================================
def customization_screen():
    """Attractive bubble-style name input screen that saves to JSON."""
    global player_data
    input_active = True
    name_text = player_data["player_name"]

    while True:
        screen.fill((15, 15, 25))

        # Title
        title_surf = font_title.render("PLAYER CUSTOMIZATION", True, (230, 20, 20))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 100))

        # Subtitle / Label
        lbl = font_menu.render("Enter Your Player Name:", True, (200, 200, 200))
        screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, 220))

        # Attractive Bubble Input Box (Pill Shape)
        bubble_rect = pygame.Rect(WIDTH // 2 - 250, 280, 500, 70)

        # Glow / Border when active
        border_color = (255, 60, 60) if input_active else (100, 100, 130)
        pygame.draw.rect(screen, (30, 30, 45), bubble_rect, border_radius=35)
        pygame.draw.rect(screen, border_color, bubble_rect, 3, border_radius=35)

        # Render Name Text inside Bubble
        display_text = name_text + ("|" if (pygame.time.get_ticks() // 500) % 2 == 0 else "")
        txt_surf = font_menu.render(display_text, True, (255, 255, 255))
        screen.blit(txt_surf, (bubble_rect.x + 30, bubble_rect.y + 20))

        # Save & Back Button
        save_rect = pygame.Rect(WIDTH // 2 - 120, 440, 240, 55)
        pygame.draw.rect(screen, (180, 10, 10), save_rect, border_radius=28)
        pygame.draw.rect(screen, (255, 100, 100), save_rect, 2, border_radius=28)
        save_txt = font_menu.render("SAVE & BACK", True, (255, 255, 255))
        screen.blit(save_txt, save_txt.get_rect(center=save_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_rect.collidepoint(event.pos):
                    player_data["player_name"] = name_text.strip() if name_text.strip() else "Player"
                    save_data(player_data)
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player_data["player_name"] = name_text.strip() if name_text.strip() else "Player"
                    save_data(player_data)
                    return
                elif event.key == pygame.K_BACKSPACE:
                    name_text = name_text[:-1]
                else:
                    if len(name_text) < 16:
                        name_text += event.unicode

        pygame.display.flip()
        clock.tick(60)


# ==========================================
# **SETTINGS SCREEN CODE**
# ==========================================
def settings_screen():
    """Allows toggling sound and background music."""
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


# ==========================================
# **MAIN MENU LOOP & RENDERING**
# ==========================================
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
                    start_game_action()
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
                        start_game_action()
                    elif choice == "CUSTOMIZATION":
                        customization_screen()
                    elif choice == "SETTINGS":
                        settings_screen()
                    elif choice == "EXIT":
                        pygame.quit()
                        sys.exit()

    pygame.display.flip()
    clock.tick(60)