import math
import sys
import os
import json
import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# 16:9 Widescreen Laptop Resolution
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape the Upside Down - Main Menu")
clock = pygame.time.Clock()

# --- INITIALIZATION & DATA MANAGEMENT ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
        "score": 0,
        "profile_pic": "assets/default_avatar.png",
        "sound": True,
        "sound_level": 5,
        "music": True,
        "music_level": 5,
        "selected_character": "Will"
    }


def save_data(data):
    os.makedirs(UI_FOLDER, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


player_data = load_data()


# --- TERMINAL ASSET VERIFICATION ---
def verify_or_prompt_asset(relative_path, asset_type="image"):
    full_path = os.path.join(BASE_DIR, relative_path)
    if not os.path.exists(full_path):
        alt_path = os.path.join(BASE_DIR, "..", relative_path)
        if os.path.exists(alt_path):
            return alt_path

        print("\n" + "=" * 60)
        print(f"[!] MISSING {asset_type.upper()} ASSET: '{relative_path}'")
        print("=" * 60)
        user_input = input(f"-> Enter path for {relative_path} (or press Enter for fallback): ").strip()
        if user_input and os.path.exists(user_input):
            return user_input
        return None
    return full_path


# Load Background (Supporting both trees.jpg and trees.jpeg)
IMAGE_FILENAME = verify_or_prompt_asset(os.path.join("assets", "trees.jpg"), "background image")
if not IMAGE_FILENAME:
    IMAGE_FILENAME = verify_or_prompt_asset(os.path.join("assets", "trees.jpeg"), "background image")

bg_original = None
if IMAGE_FILENAME and os.path.exists(IMAGE_FILENAME):
    try:
        bg_original = pygame.image.load(IMAGE_FILENAME).convert()
    except Exception as e:
        print(f"[!] Error loading image: {e}")

# Fallback background if image is missing
if bg_original is None:
    print("[+] Generating procedural fallback dark-forest background...")
    bg_original = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color = (max(0, 30 - int(y * 0.03)), 5, max(0, 15 - int(y * 0.02)))
        pygame.draw.line(bg_original, color, (0, y), (WIDTH, y))

MUSIC_FILENAME = verify_or_prompt_asset(os.path.join("assets", "music.mp3"), "background music")

# Menu Options (Bottom horizontal 3 buttons)
options = ["START GAME", "CUSTOMIZATION", "SETTINGS"]
selected_option = 0

# Fonts
font_menu = pygame.font.Font(None, 30)
font_title = pygame.font.Font(None, 68)
font_small = pygame.font.Font(None, 20)


# --- MUSIC HANDLER ---
def update_music_state():
    if player_data["music"] and MUSIC_FILENAME and os.path.exists(MUSIC_FILENAME):
        try:
            pygame.mixer.music.set_volume(player_data["music_level"] / 10.0)
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(MUSIC_FILENAME)
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Music error: {e}")
    else:
        try:
            pygame.mixer.music.pause()
        except:
            pass


update_music_state()

zoom_progress = 0.0
speed = 0.0015


# --- UI DRAWING HELPER FUNCTIONS ---

def draw_styled_button(surface, text, center_x, center_y, width, height, is_selected):
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
        pygame.draw.circle(surface, border_color, (rect.left - 12, rect.centery), 5)
        pygame.draw.circle(surface, border_color, (rect.right + 12, rect.centery), 5)

    text_surface = font_menu.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)
    return rect


def draw_top_left_profile_box(surface, data, x=25, y=25):
    """Draws top-left box with Star icon, Username, Score, Profile Pic, and Option/Settings Icon."""
    box_w, box_h = 280, 75
    rect = pygame.Rect(x, y, box_w, box_h)

    bg_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg_surface.fill((15, 15, 25, 200))
    surface.blit(bg_surface, rect.topleft)
    pygame.draw.rect(surface, (180, 40, 40), rect, 2, border_radius=8)

    # Avatar / Profile Picture thumbnail
    avatar_rect = pygame.Rect(x + 10, y + 10, 55, 55)
    pygame.draw.rect(surface, (40, 40, 60), avatar_rect, border_radius=6)

    # Try loading custom profile picture if valid path provided
    pic_path = data.get("profile_pic", "")
    avatar_loaded = False
    if pic_path and os.path.exists(pic_path):
        try:
            avatar_img = pygame.image.load(pic_path).convert()
            avatar_img = pygame.transform.smoothscale(avatar_img, (55, 55))
            surface.blit(avatar_img, avatar_rect.topleft)
            avatar_loaded = True
        except:
            pass
    if not avatar_loaded:
        # Default placeholder avatar icon text
        av_txt = font_small.render("PIC", True, (180, 180, 180))
        surface.blit(av_txt, av_txt.get_rect(center=avatar_rect.center))

    # Star Icon & Username
    star_txt = font_menu.render("⭐", True, (255, 215, 0))
    surface.blit(star_txt, (x + 75, y + 10))

    name_surf = font_menu.render(data.get("player_name", "Player"), True, (240, 240, 240))
    surface.blit(name_surf, (x + 110, y + 12))

    # Score Display
    score_surf = font_small.render(f"Score: {data.get('score', 0)}", True, (200, 200, 200))
    surface.blit(score_surf, (x + 75, y + 42))

    # Option / Edit Button Icon (Gear or Customization trigger)
    option_rect = pygame.Rect(x + box_w - 40, y + 20, 32, 32)
    pygame.draw.rect(surface, (50, 50, 75), option_rect, border_radius=6)
    pygame.draw.rect(surface, (220, 50, 50), option_rect, 1, border_radius=6)
    gear_txt = font_small.render("⚙", True, (255, 255, 255))
    surface.blit(gear_txt, gear_txt.get_rect(center=option_rect.center))

    return option_rect


def draw_exit_button(surface, x=WIDTH - 140, y=25):
    rect = pygame.Rect(x, y, 115, 44)
    bg_surface = pygame.Surface((115, 44), pygame.SRCALPHA)
    bg_surface.fill((30, 10, 10, 200))
    surface.blit(bg_surface, rect.topleft)
    pygame.draw.rect(surface, (230, 30, 30), rect, 2, border_radius=8)

    exit_txt = font_menu.render("🚪 EXIT", True, (255, 80, 80))
    surface.blit(exit_txt, exit_txt.get_rect(center=rect.center))
    return rect


# --- POP-UP PROFILE EDIT DIALOG ---
def open_profile_dialog():
    global player_data
    active_field = "name"  # "name", "score", "pic"
    name_input = str(player_data.get("player_name", "Player"))
    score_input = str(player_data.get("score", 0))
    pic_input = str(player_data.get("profile_pic", ""))

    dialog_active = True
    d_w, d_h = 480, 340
    d_rect = pygame.Rect((WIDTH - d_w) // 2, (HEIGHT - d_h) // 2, d_w, d_h)

    name_box = pygame.Rect(d_rect.x + 140, d_rect.y + 70, 300, 38)
    score_box = pygame.Rect(d_rect.x + 140, d_rect.y + 125, 300, 38)
    pic_box = pygame.Rect(d_rect.x + 140, d_rect.y + 180, 300, 38)

    save_btn = pygame.Rect(d_rect.x + 90, d_rect.y + 270, 130, 45)
    cancel_btn = pygame.Rect(d_rect.x + 260, d_rect.y + 270, 130, 45)

    while dialog_active:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (20, 20, 32), d_rect, border_radius=12)
        pygame.draw.rect(screen, (220, 30, 30), d_rect, 2, border_radius=12)

        title_s = font_menu.render("EDIT PROFILE & STATS", True, (255, 255, 255))
        screen.blit(title_s, title_s.get_rect(center=(d_rect.centerx, d_rect.y + 30)))

        # Labels & Input boxes
        labels = [("Username:", name_box, name_input), ("Score:", score_box, score_input),
                  ("Profile Pic:", pic_box, pic_input)]

        for i, (lbl, box, val) in enumerate(labels):
            lbl_surf = font_small.render(lbl, True, (220, 220, 220))
            screen.blit(lbl_surf, (d_rect.x + 25, box.y + 10))

            is_active = (
                    (i == 0 and active_field == "name") or
                    (i == 1 and active_field == "score") or
                    (i == 2 and active_field == "pic")
            )
            border_col = (255, 80, 80) if is_active else (80, 80, 110)
            pygame.draw.rect(screen, (10, 10, 15), box, border_radius=6)
            pygame.draw.rect(screen, border_col, box, 2, border_radius=6)

            val_surf = font_small.render(val, True, (255, 215, 0))
            screen.blit(val_surf, (box.x + 10, box.y + 10))

        # Save & Cancel Buttons
        pygame.draw.rect(screen, (180, 20, 20), save_btn, border_radius=6)
        save_t = font_menu.render("SAVE", True, (255, 255, 255))
        screen.blit(save_t, save_t.get_rect(center=save_btn.center))

        pygame.draw.rect(screen, (60, 60, 80), cancel_btn, border_radius=6)
        cancel_t = font_menu.render("CANCEL", True, (255, 255, 255))
        screen.blit(cancel_t, cancel_t.get_rect(center=cancel_btn.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if name_box.collidepoint(pos):
                    active_field = "name"
                elif score_box.collidepoint(pos):
                    active_field = "score"
                elif pic_box.collidepoint(pos):
                    active_field = "pic"
                elif save_btn.collidepoint(pos):
                    player_data["player_name"] = name_input.strip() or "Player"
                    try:
                        player_data["score"] = int(score_input.strip())
                    except:
                        pass
                    player_data["profile_pic"] = pic_input.strip()
                    save_data(player_data)
                    dialog_active = False
                elif cancel_btn.collidepoint(pos):
                    dialog_active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player_data["player_name"] = name_input.strip() or "Player"
                    try:
                        player_data["score"] = int(score_input.strip())
                    except:
                        pass
                    player_data["profile_pic"] = pic_input.strip()
                    save_data(player_data)
                    dialog_active = False
                elif event.key == pygame.K_ESCAPE:
                    dialog_active = False
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "name":
                        name_input = name_input[:-1]
                    elif active_field == "score":
                        score_input = score_input[:-1]
                    elif active_field == "pic":
                        pic_input = pic_input[:-1]
                else:
                    if event.unicode.isprintable():
                        if active_field == "name" and len(name_input) < 14:
                            name_input += event.unicode
                        elif active_field == "score" and len(score_input) < 8:
                            score_input += event.unicode
                        elif active_field == "pic" and len(pic_input) < 60:
                            pic_input += event.unicode

        pygame.display.flip()
        clock.tick(60)


# ==========================================
# **START GAME ACTION**
# ==========================================
def start_game_action():
    global zoom_progress
    thunder_path = verify_or_prompt_asset(os.path.join("assets", "thunder.mp3"), "thunder sound")
    thunder_sound = None
    try:
        if thunder_path and os.path.exists(thunder_path):
            thunder_sound = pygame.mixer.Sound(thunder_path)
    except:
        pass

    warning_active = True
    flash_timer = 0
    flash_alpha = 0

    while warning_active:
        flash_timer += 1
        if flash_timer % 110 == 0:
            flash_alpha = 200
            if thunder_sound and player_data["sound"]:
                thunder_sound.play()
        if flash_alpha > 0:
            flash_alpha -= 12

        screen.fill((min(255, 10 + flash_alpha), 0, 0))

        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        vignette.fill((15, 0, 0, 230))
        screen.blit(vignette, (0, 0))

        title_s = font_title.render("WARNING: ENTERING THE RIFT", True, (255, 40, 40))
        t1 = font_menu.render("You are crossing into the unstable Upside Down dimension.", True, (220, 220, 220))
        prompt = font_small.render("[ PRESS ENTER OR CLICK TO START ]", True, (255, 255, 255))

        screen.blit(title_s, title_s.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
        screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))

        if (pygame.time.get_ticks() // 400) % 2 == 0:
            screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                warning_active = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                warning_active = False

    try:
        import main
        if hasattr(main, 'run_game'):
            main.run_game(screen, player_data)
        else:
            print("Error: main.py mein 'run_game(screen, player_data)' function nahi mila.")
    except ImportError:
        print("Error: main.py file nahi mili root directory mein!")


# ==========================================
# **CUSTOMIZATION SCREEN**
# ==========================================
def customization_screen():
    """Customization screen loading shape options or custom UI parameters."""
    running_custom = True
    while running_custom:
        screen.fill((20, 20, 30))
        title = font_title.render("CUSTOMIZATION", True, (230, 30, 30))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))

        info = font_menu.render("Select Character / Shape (Shape 1 Active)", True, (240, 240, 240))
        screen.blit(info, info.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

        back_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 150, 200, 50)
        pygame.draw.rect(screen, (50, 50, 70), back_rect, border_radius=6)
        pygame.draw.rect(screen, (220, 30, 30), back_rect, 2, border_radius=6)
        b_txt = font_menu.render("BACK", True, (255, 255, 255))
        screen.blit(b_txt, b_txt.get_rect(center=back_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and back_rect.collidepoint(event.pos):
                running_custom = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_custom = False

        pygame.display.flip()
        clock.tick(60)


# ==========================================
# **SETTINGS SCREEN (Music & Sound levels)**
# ==========================================
def settings_screen():
    global player_data
    running_settings = True
    while running_settings:
        screen.fill((15, 15, 25))
        title = font_title.render("SETTINGS", True, (230, 30, 30))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))

        # Sound & Music Toggles & Level controls
        sound_status = f"Sound Effects: {'ON' if player_data['sound'] else 'OFF'} (Level: {player_data['sound_level']})"
        music_status = f"Background Music: {'ON' if player_data['music'] else 'OFF'} (Level: {player_data['music_level']})"

        sound_rect = pygame.Rect(WIDTH // 2 - 250, 220, 500, 55)
        music_rect = pygame.Rect(WIDTH // 2 - 250, 300, 500, 55)

        pygame.draw.rect(screen, (30, 30, 45), sound_rect, border_radius=6)
        pygame.draw.rect(screen, (30, 30, 45), music_rect, border_radius=6)

        screen.blit(font_menu.render(sound_status, True, (240, 240, 240)), (sound_rect.x + 20, sound_rect.y + 15))
        screen.blit(font_menu.render(music_status, True, (240, 240, 240)), (music_rect.x + 20, music_rect.y + 15))

        # Instructions for level adjustments
        inst = font_small.render("Click box to toggle ON/OFF. Press UP/DOWN arrow keys or scroll to adjust levels.",
                                 True, (160, 160, 180))
        screen.blit(inst, inst.get_rect(center=(WIDTH // 2, 400)))

        back_rect = pygame.Rect(WIDTH // 2 - 100, 480, 200, 50)
        pygame.draw.rect(screen, (50, 50, 70), back_rect, border_radius=6)
        pygame.draw.rect(screen, (230, 30, 30), back_rect, 2, border_radius=6)
        screen.blit(font_menu.render("BACK", True, (255, 255, 255)), back_rect.get_rect(center=back_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if sound_rect.collidepoint(event.pos):
                    player_data["sound"] = not player_data["sound"]
                elif music_rect.collidepoint(event.pos):
                    player_data["music"] = not player_data["music"]
                    update_music_state()
                elif back_rect.collidepoint(event.pos):
                    save_data(player_data)
                    running_settings = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player_data["music_level"] = min(10, player_data["music_level"] + 1)
                    player_data["sound_level"] = min(10, player_data["sound_level"] + 1)
                    update_music_state()
                elif event.key == pygame.K_DOWN:
                    player_data["music_level"] = max(0, player_data["music_level"] - 1)
                    player_data["sound_level"] = max(0, player_data["sound_level"] - 1)
                    update_music_state()
                elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    save_data(player_data)
                    running_settings = False

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

    # Seamless Zoom Background Effect
    scale1 = 1.0 + zoom_progress
    w1, h1 = int(WIDTH * scale1), int(HEIGHT * scale1)
    surf1 = pygame.transform.smoothscale(bg_original, (w1, h1))
    alpha1 = int((1.0 - zoom_progress) * 255)
    surf1.set_alpha(alpha1)
    screen.blit(surf1, ((WIDTH - w1) // 2, (HEIGHT - h1) // 2))

    scale2 = 1.0 + zoom_progress
    scale2 = scale2 + 0.5 if zoom_progress < 0.5 else scale2 - 0.5