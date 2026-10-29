import os
import sys
import pygame

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stranger Things - Game Over UI")
clock = pygame.time.Clock()


class AestheticHorrorGameOver:

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h

        # BG4.jpeg load karna
        self.bg_image = None
        if os.path.exists("BG4.jpeg"):
            try:
                raw_bg = pygame.image.load("BG4.jpeg").convert()
                self.bg_image = pygame.transform.scale(
                    raw_bg, (self.sw, self.sh)
                )
            except Exception as e:
                print("BG4.jpeg load nahi ho saka:", e)

        # Fonts
        self.title_font = pygame.font.SysFont("georgia", 32, bold=True)
        self.quote_font = pygame.font.SysFont("georgia", 16, italic=True)
        self.stat_font = pygame.font.SysFont("arial", 22)
        self.btn_font = pygame.font.SysFont("arial", 20, bold=True)

        # Buttons Setup
        btn_w, btn_h = 240, 48
        center_x = self.sw // 2 - btn_w // 2

        self.btn_restart = pygame.Rect(center_x, 340, btn_w, btn_h)
        self.btn_menu = pygame.Rect(center_x, 405, btn_w, btn_h)
        self.btn_quit = pygame.Rect(center_x, 470, btn_w, btn_h)

    def draw(self, surface, final_score=1250, max_lives=5):
        # 1. Background Image (BG4.jpeg)
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((10, 10, 15))

        # 2. Dark Reddish Overlay (No Box)
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((5, 2, 8, 225))
        surface.blit(overlay, (0, 0))

        # 3. Header Title
        title_surf = self.title_font.render(
            "FEET FROM FREEDOM", True, (210, 20, 30)
        )
        title_rect = title_surf.get_rect(center=(self.sw // 2, 90))
        surface.blit(title_surf, title_rect)

        # 4. Captions
        q1_surf = self.quote_font.render(
            '"The gate closes behind you forever..."', True, (160, 150, 170)
        )
        q2_surf = self.quote_font.render(
            "The darkness didn't catch you... it was waiting for you.",
            True,
            (190, 50, 60),
        )

        surface.blit(q1_surf, q1_surf.get_rect(center=(self.sw // 2, 140)))
        surface.blit(q2_surf, q2_surf.get_rect(center=(self.sw // 2, 168)))

        # Separator Line
        pygame.draw.line(
            surface,
            (90, 20, 30),
            (self.sw // 2 - 200, 200),
            (self.sw // 2 + 200, 200),
            2,
        )

        # 5. Stats
        score_surf = self.stat_font.render(
            f"FINAL SCORE : {int(final_score)}", True, (220, 220, 230)
        )
        lives_surf = self.stat_font.render(
            f"LIVES REMAINING : 0 / {max_lives}", True, (150, 40, 50)
        )

        surface.blit(
            score_surf, score_surf.get_rect(center=(self.sw // 2, 240))
        )
        surface.blit(
            lives_surf, lives_surf.get_rect(center=(self.sw // 2, 275))
        )

        # 6. Interactive Buttons
        mouse_pos = pygame.mouse.get_pos()
        buttons = [
            (self.btn_restart, "TRY AGAIN [R]", (140, 20, 30)),
            (self.btn_menu, "MAIN MENU [M]", (35, 35, 50)),
            (self.btn_quit, "GIVE UP [Q]", (25, 25, 35)),
        ]

        for rect, label, base_color in buttons:
            is_hovered = rect.collidepoint(mouse_pos)
            if is_hovered:
                color = (
                    min(base_color[0] + 50, 255),
                    min(base_color[1] + 50, 255),
                    min(base_color[2] + 50, 255),
                )
                border_color = (220, 30, 40)
            else:
                color = base_color
                border_color = (100, 30, 40)

            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(
                surface, border_color, rect, width=2, border_radius=6
            )

            text_surf = self.btn_font.render(label, True, (240, 240, 240))
            surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return "restart"
            elif event.key == pygame.K_m:
                return "menu"
            elif event.key == pygame.K_q:
                return "quit"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_restart.collidepoint(event.pos):
                return "restart"
            elif self.btn_menu.collidepoint(event.pos):
                return "menu"
            elif self.btn_quit.collidepoint(event.pos):
                return "quit"

        return None


if __name__ == "__main__":
    game_over_ui = AestheticHorrorGameOver(WIDTH, HEIGHT)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            action = game_over_ui.handle_input(event)
            if action == "restart":
                print("Action: Restart")
            elif action == "menu":
                print("Action: Menu")
            elif action == "quit":
                running = False

        game_over_ui.draw(screen, final_score=1450, max_lives=5)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()