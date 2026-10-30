import os
import pygame

# --- HIGH SCORE LOADER IMPORT ---
try:
    from UI.high_score_mngr import load_high_score
except ImportError:
    from high_score_mngr import load_high_score


class AestheticHorrorGameOver:

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h

        # BG4.jpeg background loading
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
        self.stat_font = pygame.font.SysFont("arial", 20)
        self.high_score_font = pygame.font.SysFont("arial", 22, bold=True)
        self.btn_font = pygame.font.SysFont("arial", 20, bold=True)

        # Interactive Buttons Setup
        btn_w, btn_h = 250, 50
        center_x = (self.sw // 2) - (btn_w // 2)

        self.btn_restart = pygame.Rect(center_x, 370, btn_w, btn_h)
        self.btn_quit = pygame.Rect(center_x, 435, btn_w, btn_h)

    def draw(self, surface, final_score=0, max_lives=5):
        # 1. Background Image
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((10, 10, 15))

        # 2. Dark Overlay
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((5, 2, 8, 225))
        surface.blit(overlay, (0, 0))

        # 3. Header Title
        title_surf = self.title_font.render(
            "FEET FROM FREEDOM", True, (210, 20, 30)
        )
        title_rect = title_surf.get_rect(center=(self.sw // 2, 80))
        surface.blit(title_surf, title_rect)

        # 4. Horror Captions
        q1_surf = self.quote_font.render(
            '"The gate closes behind you forever..."', True, (160, 150, 170)
        )
        q2_surf = self.quote_font.render(
            "The darkness didn't catch you... it was waiting for you.",
            True,
            (190, 50, 60),
        )

        surface.blit(q1_surf, q1_surf.get_rect(center=(self.sw // 2, 125)))
        surface.blit(q2_surf, q2_surf.get_rect(center=(self.sw // 2, 150)))

        # Separator Line
        pygame.draw.line(
            surface,
            (90, 20, 30),
            ((self.sw // 2) - 200, 180),
            ((self.sw // 2) + 200, 180),
            2,
        )

        # 5. Load High Score from JSON
        high_score = load_high_score()

        # 6. Stats & High Score Display
        score_surf = self.stat_font.render(
            f"FINAL SCORE : {int(final_score)}", True, (220, 220, 230)
        )
        best_surf = self.high_score_font.render(
            f"BEST HIGH SCORE : {int(high_score)}", True, (255, 215, 0)
        )
        lives_surf = self.stat_font.render(
            f"LIVES REMAINING : 0 / {max_lives}", True, (150, 40, 50)
        )

        surface.blit(
            score_surf, score_surf.get_rect(center=(self.sw // 2, 215))
        )
        surface.blit(
            best_surf, best_surf.get_rect(center=(self.sw // 2, 255))
        )
        surface.blit(
            lives_surf, lives_surf.get_rect(center=(self.sw // 2, 295))
        )

        # 7. Buttons Drawing
        mouse_pos = pygame.mouse.get_pos()
        buttons = [
            (self.btn_restart, "TRY AGAIN [R]", (140, 20, 30)),
            (self.btn_quit, "GIVE UP [Q]", (35, 35, 50)),
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
            elif event.key in (pygame.K_q, pygame.K_m, pygame.K_ESCAPE):
                return "menu"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_restart.collidepoint(event.pos):
                return "restart"
            elif self.btn_quit.collidepoint(event.pos):
                return "menu"

        return None