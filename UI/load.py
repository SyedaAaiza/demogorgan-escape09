import os
import sys
import time
import random
import pygame

# Get directory paths for relative asset loading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")

# Clean standard import since you renamed it with an underscore
from menu_pg import MainMenu

GAME_TITLE = "DEMOGORGON ESCAPE"

pygame.init()
pygame.mixer.init()

display_info = pygame.display.Info()
WIDTH, HEIGHT = display_info.current_w, display_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()

IMAGE_FILENAME = os.path.join(ASSETS_DIR, "bgfizz.jpeg")
AUDIO_FILENAME = os.path.join(ASSETS_DIR, "s1.mpeg")

try:
    bg_image = pygame.image.load(IMAGE_FILENAME).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Error: '{IMAGE_FILENAME}' not found! Details: {e}")
    pygame.quit()
    sys.exit()

# Load and loop custom monster audio file infinitely
try:
    pygame.mixer.music.load(AUDIO_FILENAME)
    pygame.mixer.music.play(loops=-1)
except Exception as e:
    print(f"Audio Warning: Could not load '{AUDIO_FILENAME}'. Details: {e}")

load_font = pygame.font.SysFont("Courier New", max(16, HEIGHT // 35), bold=True)

# Lightning visual strike variables
lightning_active = False
lightning_timer = time.time()
next_lightning_time = random.uniform(0.3, 0.9)
lightning_duration = 0
bolt_segments = []


def create_lightning_bolt():
    start_x = random.randint(int(WIDTH * 0.1), int(WIDTH * 0.9))
    start_y = 0
    segments = [(start_x, start_y)]

    current_x, current_y = start_x, start_y
    while current_y < HEIGHT * 0.75:
        next_y = current_y + random.randint(30, 70)
        next_x = current_x + random.randint(-60, 60)
        segments.append((next_x, next_y))
        current_x, current_y = next_x, next_y

    return segments


def run_loading_screen():
    global lightning_active, lightning_timer, next_lightning_time, lightning_duration, bolt_segments

    start_time = time.time()
    running = True

    while running:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Continuous lightning bolt triggers
        if current_time - lightning_timer > next_lightning_time:
            lightning_active = True
            lightning_duration = random.uniform(0.08, 0.18)
            bolt_segments = create_lightning_bolt()
            lightning_timer = current_time
            next_lightning_time = random.uniform(0.4, 1.2)

        if lightning_active and (current_time - lightning_timer > lightning_duration):
            lightning_active = False

        # Draw background image
        screen.blit(bg_image, (0, 0))

        # Draw visual jagged lightning strikes
        if lightning_active and len(bolt_segments) > 1:
            pygame.draw.lines(screen, (255, 60, 60), False, bolt_segments, 10)
            pygame.draw.lines(screen, (255, 255, 255), False, bolt_segments, 4)

        center_x, center_y = WIDTH // 2, HEIGHT // 2

        # Calculate progress over 5 seconds
        elapsed = current_time - start_time
        loading_progress = int(min(100, (elapsed / 5.0) * 100))

        # Render loading text
        load_surface = load_font.render(f"CONNECTING TO UPSIDE DOWN... {loading_progress}%", True, (220, 30, 40))
        load_rect = load_surface.get_rect(center=(center_x, HEIGHT * 0.85))

        bar_width = int(WIDTH * 0.4)
        bar_height = int(HEIGHT * 0.025)
        bar_x = center_x - (bar_width // 2)
        bar_y = int(HEIGHT * 0.90)

        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (loading_progress / 100))
        pygame.draw.rect(screen, (220, 30, 40), (bar_x, bar_y, fill_width, bar_height))

        # Moving Bicycle Icon
        cycle_x = bar_x + fill_width
        cycle_y = bar_y - 12
        pygame.draw.circle(screen, (200, 200, 200), (cycle_x - 8, cycle_y + 10), 6, 2)
        pygame.draw.circle(screen, (200, 200, 200), (cycle_x + 8, cycle_y + 10), 6, 2)
        pygame.draw.line(screen, (220, 30, 40), (cycle_x - 8, cycle_y + 10), (cycle_x, cycle_y + 2), 2)
        pygame.draw.line(screen, (220, 30, 40), (cycle_x + 8, cycle_y + 10), (cycle_x, cycle_y + 2), 2)
        pygame.draw.line(screen, (220, 30, 40), (cycle_x - 12, cycle_y + 2), (cycle_x + 4, cycle_y + 2), 2)

        screen.blit(load_surface, load_rect)

        pygame.display.flip()
        clock.tick(60)

        # As soon as the loading bar hits 100%, transition into the Main Menu seamlessly
        if loading_progress >= 100:
            pygame.time.delay(400)
            menu = MainMenu(screen, clock)
            menu.run()
            return


if __name__ == "__main__":
    run_loading_screen()