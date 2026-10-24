import sys
import os
import pygame

# Initialize Pygame & Mixer
pygame.init()
pygame.mixer.init()

# Fullscreen Mode Setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Escape the Upside Down - Main Menu")

CLOCK = pygame.time.Clock()
FPS = 60

# --- COLOR PALETTE ---
COLOR_RED = (220, 20, 60)
COLOR_NEON_RED = (255, 45, 0)
COLOR_DARK_RED = (80, 0, 0)
COLOR_WHITE = (245, 245, 245)
COLOR_LIGHT_GRAY = (190, 190, 200)

# --- HORROR & STYLISH FONT LOADING ---
# Tip: Aap koi bhi horror .ttf font download karke 'assets/horror_font.ttf' ke naam se rakh sakte hain!
possible_font_paths = [
    os.path.join("..", "assets", "horror_font.ttf"),
    os.path.join("assets", "horror_font.ttf")
]

FONT_BUTTON = None
FONT_BODY = None

for fpath in possible_font_paths:
    if os.path.exists(fpath):
        try:
            FONT_BUTTON = pygame.font.Font(fpath, 22)
            FONT_BODY = pygame.font.Font(fpath, 20)
            break
        except:
            pass

# Fallback to stylish/horror system fonts if custom .ttf is not found
if not FONT_BUTTON:
    try:
        # 'Chiller' ya 'Impact' Windows ke kaafi dramatic aur horror-style fonts hain
        FONT_BUTTON = pygame.font.SysFont("chiller", 30, bold=True)
    except:
        FONT_BUTTON = pygame.font.SysFont("impact", 24)

if not FONT_BODY:
    FONT_BODY = pygame.font.SysFont("consolas", 22)

FONT_COUNTDOWN = pygame.font.SysFont("impact", 120)

# --- LOAD BACKGROUND ASSET ---
BG_PATH = os.path.join("..", "assets", "trees.jpeg")
if not os.path.exists(BG_PATH):
    if os.path.exists(os.path.join("assets", "trees.jpeg")):
        BG_PATH = os.path.join("assets", "trees.jpeg")

if os.path.exists(BG_PATH):
    base_bg = pygame.image.load(BG_PATH).convert()
    base_bg = pygame.transform.scale(base_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    base_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    base_bg.fill((15, 10, 20))

# Zoom Variables (Fast & Smooth)
zoom_scale = 1.0
zoom_direction = 1
zoom_speed = 0.0006

# --- GLOBAL SETTINGS STATE ---
sound_volume = 5
sound_muted = False


# ==========================================
# BUTTON CLASS (Fully Rounded / Pill Shape)
# ==========================================
class Button:
    def __init__(self, text, x, y, width, height, is_icon=False):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.is_icon = is_icon

    def draw(self, surface):
        if self.is_hovered:
            border_color = COLOR_NEON_RED
            text_color = COLOR_WHITE
            bg_alpha = 200
        else:
            border_color = COLOR_DARK_RED
            text_color = COLOR_LIGHT_GRAY
            bg_alpha = 140

        btn_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        radius = self.rect.height // 2
        pygame.draw.rect(btn_surface, (10, 10, 15, bg_alpha), (0, 0, self.rect.width, self.rect.height),
                         border_radius=radius)
        surface.blit(btn_surface, self.rect.topleft)

        pygame.draw.rect(surface, border_color, self.rect, width=3, border_radius=radius)

        if self.is_icon:
            cx, cy = self.rect.center
            offset = 8
            pygame.draw.line(surface, text_color, (cx - offset, cy - offset), (cx + offset, cy + offset), 3)
            pygame.draw.line(surface, text_color, (cx - offset, cy + offset), (cx + offset, cy - offset), 3)
        else:
            text_surf = FONT_BUTTON.render(self.text, True, text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def is_clicked(self, mouse_pos, event):
        return self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1


# ==========================================
# HELPER: WARNING PAGE & 3, 2, 1 COUNTDOWN
# ==========================================
def show_warning_and_countdown():
    global zoom_scale, zoom_direction
    showing_warning = True
    start_btn = Button("ENTER THE SHADOWS", SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 150, 280, 52)

    while showing_warning:
        mouse_pos = pygame.mouse.get_pos()
        start_btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if start_btn.is_clicked(mouse_pos, event) or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
            ):
                showing_warning = False

        zoom_scale += zoom_speed * zoom_direction
        if zoom_scale >= 1.35:
            zoom_direction = -1
        elif zoom_scale <= 1.0:
            zoom_direction = 1

        current_w = int(SCREEN_WIDTH * zoom_scale)
        current_h = int(SCREEN_HEIGHT * zoom_scale)
        scaled_bg = pygame.transform.smoothscale(base_bg, (current_w, current_h))

        bg_x = (SCREEN_WIDTH - current_w) // 2
        bg_y = (SCREEN_HEIGHT - current_h) // 2

        screen.blit(scaled_bg, (bg_x, bg_y))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        screen.blit(overlay, (0, 0))

        title_surf = FONT_BUTTON.render("WARNING: THE UPSIDE DOWN AWAITS", True, COLOR_RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.22)))
        screen.blit(title_surf, title_rect)

        lines = [
            "You are about to cross into a dark, corrupted realm.",
            "Demogorgons and shadows lurk in the mist.",
            "Make sure your controls and defenses are ready.",
            "",
            "Press ENTER or click below to proceed..."
        ]

        for idx, line in enumerate(lines):
            line_surf = FONT_BODY.render(line, True, COLOR_WHITE if idx == 4 else COLOR_LIGHT_GRAY)
            line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.38) + idx * 45))
            screen.blit(line_surf, line_rect)

        start_btn.draw(screen)
        pygame.display.flip()
        CLOCK.tick(FPS)

    # --- COUNTDOWN ---
    for count in [3, 2, 1]:
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 900:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.blit(base_bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 225))
            screen.blit(overlay, (0, 0))

            num_surf = FONT_COUNTDOWN.render(str(count), True, COLOR_NEON_RED)
            num_rect = num_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(num_surf, num_rect)

            pygame.display.flip()
            CLOCK.tick(FPS)


# ==========================================
# PAGE CONNECTORS
# ==========================================
def launch_main_game():
    show_warning_and_countdown()
    try:
        import main
        if hasattr(main, 'run'):
            main.run()
        elif hasattr(main, 'main'):
            main.main()
    except ImportError as e:
        print(f"[ERROR] Could not import main.py: {e}")


def launch_customization():
    try:
        import custom
        if hasattr(custom, 'run'):
            custom.run()
        elif hasattr(custom, 'main'):
            custom.main()
    except ImportError as e:
        print(f"[ERROR] Could not import custom.py: {e}")


# ==========================================
# SETTINGS SCREEN
# ==========================================
def open_settings():
    global sound_volume, sound_muted, zoom_scale, zoom_direction
    in_settings = True

    back_btn = Button("BACK TO MENU", SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT - 150, 220, 50)
    vol_down_btn = Button("-", SCREEN_WIDTH // 2 - 120, int(SCREEN_HEIGHT * 0.48), 48, 48)
    vol_up_btn = Button("+", SCREEN_WIDTH // 2 + 75, int(SCREEN_HEIGHT * 0.48), 48, 48)
    mute_btn = Button("TOGGLE MUTE", SCREEN_WIDTH // 2 - 100, int(SCREEN_HEIGHT * 0.62), 200, 48)

    while in_settings:
        mouse_pos = pygame.mouse.get_pos()
        for btn in [back_btn, vol_down_btn, vol_up_btn, mute_btn]:
            btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                in_settings = False

            if back_btn.is_clicked(mouse_pos, event):
                in_settings = False

            if vol_down_btn.is_clicked(mouse_pos, event):
                sound_volume = max(0, sound_volume - 1)
                pygame.mixer.music.set_volume(0 if sound_muted else sound_volume / 10.0)

            if vol_up_btn.is_clicked(mouse_pos, event):
                sound_volume = min(10, sound_volume + 1)
                pygame.mixer.music.set_volume(0 if sound_muted else sound_volume / 10.0)

            if mute_btn.is_clicked(mouse_pos, event):
                sound_muted = not sound_muted
                pygame.mixer.music.set_volume(0 if sound_muted else sound_volume / 10.0)

        zoom_scale += zoom_speed * zoom_direction
        if zoom_scale >= 1.35:
            zoom_direction = -1
        elif zoom_scale <= 1.0:
            zoom_direction = 1

        current_w = int(SCREEN_WIDTH * zoom_scale)
        current_h = int(SCREEN_HEIGHT * zoom_scale)
        scaled_bg = pygame.transform.smoothscale(base_bg, (current_w, current_h))

        bg_x = (SCREEN_WIDTH - current_w) // 2
        bg_y = (SCREEN_HEIGHT - current_h) // 2

        screen.blit(scaled_bg, (bg_x, bg_y))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 12, 220))
        screen.blit(overlay, (0, 0))

        title = FONT_BUTTON.render("AUDIO SETTINGS", True, COLOR_RED)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.2))))

        status_text = "MUTED" if sound_muted else f"{sound_volume} / 10"
        vol_label = FONT_BODY.render(f"Sound Level:  [ {status_text} ]", True, COLOR_WHITE)
        screen.blit(vol_label, vol_label.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.38))))

        vol_down_btn.draw(screen)
        vol_up_btn.draw(screen)
        mute_btn.draw(screen)
        back_btn.draw(screen)

        pygame.display.flip()
        CLOCK.tick(FPS)


# ==========================================
# MAIN MENU LOOP
# ==========================================
def main_menu():
    global zoom_scale, zoom_direction

    btn_w, btn_h = 240, 50
    center_x = SCREEN_WIDTH // 2

    # Perfect bottom positioning
    start_y = SCREEN_HEIGHT - 170
    btn_start = Button("START", center_x - btn_w // 2, start_y, btn_w, btn_h)

    sub_y = start_y + 62
    gap = 25
    btn_custom = Button("CUSTOMIZATION", center_x - btn_w - gap // 2, sub_y, btn_w, btn_h)
    btn_settings = Button("SETTINGS", center_x + gap // 2, sub_y, btn_w, btn_h)

    # Top-right cross icon button for Exit
    btn_exit = Button("", SCREEN_WIDTH - 70, 30, 45, 45, is_icon=True)

    buttons = [btn_start, btn_custom, btn_settings, btn_exit]

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for btn in buttons:
            btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if btn_start.is_clicked(mouse_pos, event):
                launch_main_game()

            elif btn_custom.is_clicked(mouse_pos, event):
                launch_customization()

            elif btn_settings.is_clicked(mouse_pos, event):
                open_settings()

            elif btn_exit.is_clicked(mouse_pos, event):
                running = False

        zoom_scale += zoom_speed * zoom_direction
        if zoom_scale >= 1.35:
            zoom_direction = -1
        elif zoom_scale <= 1.0:
            zoom_direction = 1

        current_w = int(SCREEN_WIDTH * zoom_scale)
        current_h = int(SCREEN_HEIGHT * zoom_scale)
        scaled_bg = pygame.transform.smoothscale(base_bg, (current_w, current_h))

        bg_x = (SCREEN_WIDTH - current_w) // 2
        bg_y = (SCREEN_HEIGHT - current_h) // 2

        screen.blit(scaled_bg, (bg_x, bg_y))

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_menu()