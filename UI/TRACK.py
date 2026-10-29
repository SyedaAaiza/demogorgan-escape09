import os
import pygame


class Pseudo3DTrack:

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h

        # Project directory paths setup
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ASSETS_DIR = os.path.join(BASE_DIR, "assets")
        BG2_PATH = os.path.join(ASSETS_DIR, "BG2.jpeg")

        self.bg_image = None
        if os.path.exists(BG2_PATH):
            try:
                raw_img = pygame.image.load(BG2_PATH).convert()
                self.bg_image = pygame.transform.smoothscale(
                    raw_img, (self.sw, self.sh)
                )
            except Exception as e:
                print(f"Error loading BG2.jpeg: {e}")

        # Static Horizon (Tunnel mouth locked at top 44%)
        self.horizon_y = int(self.sh * 0.44)
        self.ground_h = self.sh - self.horizon_y

        # Infinite Loop Mathematical Parameters
        self.speed = 0.80  # Movement velocity
        self.z = 0.0  # Continuous distance variable

    def update(self, dt):
        # Accumulate z continuously (never resets abruptly)
        self.z += self.speed * dt

    def draw(self, surface):
        if not self.bg_image:
            surface.fill((10, 10, 20))
            return

        # 1. STILL BACKGROUND LAYER (Dark Tunnel & Upper Forest)
        # Keeps the horizon completely fixed and sharp
        surface.blit(self.bg_image, (0, 0))

        # 2. CONTINUOUS LOGARITHMIC SEAMLESS GROUND LOOP
        # Scale ratio for 1 cycle = 2.0x zoom
        max_scale = 2.0

        # Cycle 1 Progress (offset 0.0)
        cycle1 = (self.z) % 1.0
        scale1 = 1.0 + cycle1 * (max_scale - 1.0)

        # Cycle 2 Progress (offset 0.5 - perfectly phase-shifted)
        cycle2 = (self.z + 0.5) % 1.0
        scale2 = 1.0 + cycle2 * (max_scale - 1.0)

        # Render both layers sequentially to eliminate seam gaps
        self._render_ground_slice(surface, scale2)
        self._render_ground_slice(surface, scale1)

    def _render_ground_slice(self, surface, scale):
        scaled_w = int(self.sw * scale)
        scaled_h = int(self.sh * scale)

        # Crisp mathematical smoothscale
        scaled_bg = pygame.transform.smoothscale(
            self.bg_image, (scaled_w, scaled_h)
        )

        # Fixed Center Vanishing Point Alignment
        center_x = self.sw // 2
        pos_x = center_x - (scaled_w // 2)
        pos_y = int(self.horizon_y * (1.0 - scale))

        # Crop exclusively below horizon line
        src_rect = pygame.Rect(
            max(0, -pos_x),
            max(0, self.horizon_y - pos_y),
            self.sw,
            self.ground_h,
        )

        try:
            ground_sub = scaled_bg.subsurface(src_rect)
            surface.blit(ground_sub, (0, self.horizon_y))
        except ValueError:
            pass


# Standalone Test Execution
if __name__ == "__main__":
    pygame.init()

    DISP_WIDTH, DISP_HEIGHT = 1280, 720
    screen = pygame.display.set_mode((DISP_WIDTH, DISP_HEIGHT))
    pygame.display.set_caption("Exact Seamless Track Engine")
    clock = pygame.time.Clock()

    track = Pseudo3DTrack(DISP_WIDTH, DISP_HEIGHT)
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        track.update(dt)
        track.draw(screen)

        pygame.display.flip()

    pygame.quit()