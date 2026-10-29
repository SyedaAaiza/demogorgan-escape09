import sys
import os
import pygame

# Initialize Pygame & Mixer
pygame.init()
pygame.mixer.init()

# Screen Dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Escape the Upside Down - Main Menu")

CLOCK = pygame.time.Clock()
FPS = 60

# --- COLOR PALETTE ---
COLOR_RED = (220, 20, 60)
COLOR_NEON_RED = (255, 45, 0)
COLOR_DARK_RED = (80, 0, 0)
COLOR_WHITE = (245, 245, 245)
COLOR_BLACK = (10, 10, 15)
COLOR_GRAY = (70, 70, 80)
COLOR_LIGHT_GRAY = (180, 180, 190)

# --- FONTS ---
FONT_TITLE = pygame.font.SysFont("impact", 56)
FONT_BUTTON = pygame.font.SysFont("arial black", 18)
FONT_BODY = pygame.font.SysFont("consolas", 22)
FONT_COUNTDOWN = pygame.font.SysFont("impact", 120)

# --- LOAD BACKGROUND ASSET (bgfizz.jpeg) ---
BG_PATH = "bgfizz.jpeg"
if os.path.exists(BG_PATH):
    bg_image = pygame.image.load(BG_PATH)
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    # Fallback dark background if file isn't found
    bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_image.fill((15, 10, 20))

# --- GLOBAL SETTINGS STATE ---
sound_volume = 5  # Scale 0 to 10
sound_muted = False


# ==========================================
# BUTTON CLASS
# ==========================================
class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False

    def draw(self, surface):
        if self.is_hovered:
            border_color = COLOR_NEON_RED
            text_color = COLOR_WHITE
            bg_alpha = 180
        else:
            border_color = COLOR_DARK_RED
            text_color = COLOR_LIGHT_GRAY
            bg_alpha = 120

        # Semi-transparent button background
        btn_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        btn_surface.fill((10, 10, 15, bg_alpha))
        surface.blit(btn_surface, self.rect.topleft)

        # Border box
        pygame.draw.rect(surface, border_color, self.rect, width=3, border_radius=8)

        # Label Text
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
    # --- STEP 1: WARNING SCREEN ---
    showing_warning = True
    start_btn = Button("ENTER THE SHADOWS", SCREEN_WIDTH // 2 - 120, 520, 240, 50)

    while showing_warning:
        mouse_pos = pygame.mouse.get_pos()
        start_btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if start_btn.is_clicked(mouse_pos, event) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
            ):
                showing_warning = False

        # Draw background and dark overlay
        screen.blit(bg_image, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        screen.blit(overlay, (0, 0))

        # Warning Title
        title_surf = FONT_TITLE.render("WARNING: THE UPSIDE DOWN AWAITS", True, COLOR_RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(title_surf, title_rect)

        # Narrative Warning Lines
        lines = [
            "You are about to cross into a dark, corrupted realm.",
            "Demogorgons and shadows lurk in the mist.",
            "Make sure your controls and defenses are ready.",
            "",
            "Press ENTER or click below to proceed..."
        ]

        for idx, line in enumerate(lines):
            line_surf = FONT_BODY.render(line, True, COLOR_WHITE if idx == 4 else COLOR_LIGHT_GRAY)
            line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, 240 + idx * 40))
            screen.blit(line_surf, line_rect)

        start_btn.draw(screen)
        pygame.display.flip()
        CLOCK.tick(FPS)

    # --- STEP 2: 3, 2, 1 COUNTDOWN ---
    for count in [3, 2, 1]:
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 900:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.blit(bg_image, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
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
    except ImportError:
        print("[System Warning] Could not import main.py.")


def launch_customization():
    try:
        import custom
        if hasattr(custom, 'run'):
            custom.run()
        elif hasattr(custom, 'main'):
            custom.main()
    except ImportError:
        print("[System Warning] Could not import custom.py.")


# ==========================================
# SETTINGS SCREEN (0-10 LEVEL & MUTE)
# ==========================================
def open_settings():
    global sound_volume, sound_muted
    in_settings = True

    back_btn = Button("BACK TO MENU", SCREEN_WIDTH // 2 - 100, 520, 200, 45)
    vol_down_btn = Button("-", SCREEN_WIDTH // 2 - 120, 310, 45, 45)
    vol_up_btn = Button("+", SCREEN_WIDTH // 2 + 75, 310, 45, 45)
    mute_btn = Button("TOGGLE MUTE", SCREEN_WIDTH // 2 - 90, 400, 180, 45)

    while in_settings:
        mouse_pos = pygame.mouse.get_pos()
        for btn in [back_btn, vol_down_btn, vol_up_btn, mute_btn]:
            btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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

        # Draw Settings Screen
        screen.blit(bg_image, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 12, 220))
        screen.blit(overlay, (0, 0))

        title = FONT_TITLE.render("AUDIO SETTINGS", True, COLOR_RED)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        status_text = "MUTED" if sound_muted else f"{sound_volume} / 10"
        vol_label = FONT_BODY.render(f"Sound Level:  [ {status_text} ]", True, COLOR_WHITE)
        screen.blit(vol_label, vol_label.get_rect(center=(SCREEN_WIDTH // 2, 250)))

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
    btn_width, btn_height = 190, 50
    spacing = 25
    total_width = (4 * btn_width) + (3 * spacing)
    start_x = (SCREEN_WIDTH - total_width) // 2
    bottom_y = SCREEN_HEIGHT - 90  # Aligned neatly at the bottom

    btn_start = Button("START", start_x, bottom_y, btn_width, btn_height)
    btn_custom = Button("CUSTOMIZATION", start_x + (btn_width + spacing), bottom_y, btn_width, btn_height)
    btn_settings = Button("SETTINGS", start_x + 2 * (btn_width + spacing), bottom_y, btn_width, btn_height)
    btn_exit = Button("EXIT", start_x + 3 * (btn_width + spacing), bottom_y, btn_width, btn_height)

    buttons = [btn_start, btn_custom, btn_settings, btn_exit]

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for btn in buttons:
            btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if btn_start.is_clicked(mouse_pos, event):
                launch_main_game()

            elif btn_custom.is_clicked(mouse_pos, event):
                launch_customization()

            elif btn_settings.is_clicked(mouse_pos, event):
                open_settings()

            elif btn_exit.is_clicked(mouse_pos, event):
                running = False

        # Render Background & Title
        screen.blit(bg_image, (0, 0))

        title_surf = FONT_TITLE.render("ESCAPE THE UPSIDE DOWN", True, COLOR_RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 110))
        screen.blit(title_surf, title_rect)

        # Draw Bottom Buttons
        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_menu()