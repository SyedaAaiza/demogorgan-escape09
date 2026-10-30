import os
import sys
import pygame


class ProfessionalButton:
    def __init__(self, x, y, width, height, label="", base_color=(165, 15, 15), hover_color=(215, 35, 35),
                 button_type="resume"):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.base_color = base_color
        self.hover_color = hover_color
        self.button_type = button_type  # 'resume', 'restart', 'quit_door'

    def draw(self, surface, font_small):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color

        # Draw button body with dark border
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (110, 10, 10), self.rect, 2, border_radius=10)

        center_x, center_y = self.rect.center

        if self.button_type == "resume":
            tri_y = center_y - 8
            points = [(center_x - 10, tri_y - 10), (center_x - 10, tri_y + 10), (center_x + 12, tri_y)]
            pygame.draw.polygon(surface, (255, 255, 255), points)

            text_surf = font_small.render(self.label, True, (230, 230, 230))
            text_rect = text_surf.get_rect(center=(center_x, center_y + 16))
            surface.blit(text_surf, text_rect)

        elif self.button_type == "restart":
            arc_y = center_y - 8
            radius = 12
            pygame.draw.arc(surface, (255, 255, 255), (center_x - radius, arc_y - radius, radius * 2, radius * 2), 0.8,
                            5.5, 3)
            pygame.draw.polygon(surface, (255, 255, 255),
                                [(center_x + 4, arc_y - 14), (center_x + 13, arc_y - 9), (center_x + 5, arc_y - 3)])

            text_surf = font_small.render(self.label, True, (230, 230, 230))
            text_rect = text_surf.get_rect(center=(center_x, center_y + 16))
            surface.blit(text_surf, text_rect)

        elif self.button_type == "quit_door":
            door_w, door_h = 18, 28
            door_x = center_x - door_w // 2
            door_y = center_y - 20

            pygame.draw.rect(surface, (255, 255, 255), (door_x, door_y, door_w, door_h), 2)
            pygame.draw.line(surface, (255, 255, 255), (door_x + 4, door_y + door_h // 2),
                             (door_x + 9, door_y + door_h // 2), 2)

            arrow_start_x = door_x - 10
            arrow_end_x = door_x + 8
            arrow_y = door_y + door_h // 2
            pygame.draw.line(surface, (255, 255, 255), (arrow_start_x, arrow_y), (arrow_end_x, arrow_y), 2)
            pygame.draw.polygon(surface, (255, 255, 255), [(arrow_start_x + 6, arrow_y - 4), (arrow_start_x, arrow_y),
                                                           (arrow_start_x + 6, arrow_y + 4)])

            text_surf = font_small.render(self.label, True, (230, 230, 230))
            text_rect = text_surf.get_rect(center=(center_x, center_y + 16))
            surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class PauseMenu:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height

        # Typography
        self.font_large = pygame.font.SysFont("Helvetica", 52, bold=True)
        self.font_medium = pygame.font.SysFont("Helvetica", 26, bold=True)
        self.font_small = pygame.font.SysFont("Helvetica", 16, bold=True)
        self.font_countdown = pygame.font.SysFont("Impact", 140)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "..", "assets")

        # Load Sound Effect (s1.mpeg)
        sound_path = os.path.join(assets_dir, "s1.mpeg")
        self.sound = None
        try:
            if os.path.exists(sound_path):
                self.sound = pygame.mixer.Sound(sound_path)
        except pygame.error as e:
            print(f"Note: Could not load sound ({e})")

        # Menu Buttons Configuration (Exact Center Alignment)
        btn_width, btn_height = 300, 55
        center_x = (self.width - btn_width) // 2
        RED_BASE = (165, 15, 15)
        RED_HOVER = (215, 35, 35)

        start_y = (self.height // 2) - 10
        gap = 70

        self.resume_btn = ProfessionalButton(center_x, start_y, btn_width, btn_height, label="RESUME",
                                             base_color=RED_BASE, hover_color=RED_HOVER, button_type="resume")
        self.restart_btn = ProfessionalButton(center_x, start_y + gap, btn_width, btn_height, label="RESTART",
                                              base_color=RED_BASE, hover_color=RED_HOVER, button_type="restart")
        self.quit_btn = ProfessionalButton(center_x, start_y + (gap * 2), btn_width, btn_height, label="QUIT TO MENU",
                                           base_color=RED_BASE, hover_color=RED_HOVER, button_type="quit_door")

    def play_audio(self):
        if self.sound:
            self.sound.play()

    def run(self, surface, current_score, clock, disp_width, disp_height, game_surface):
        self.play_audio()

        scaled_snapshot = pygame.transform.smoothscale(game_surface, (disp_width, disp_height))

        running = True
        action = None

        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.resume_btn.is_clicked(event):
                    action = "RESUME"
                    running = False
                elif self.restart_btn.is_clicked(event):
                    action = "RESTART"
                    running = False
                elif self.quit_btn.is_clicked(event):
                    action = "QUIT"
                    running = False

            # Draw frozen background snapshot
            surface.blit(scaled_snapshot, (0, 0))

            # Dark overlay
            overlay = pygame.Surface((disp_width, disp_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            surface.blit(overlay, (0, 0))

            # GAME PAUSED Title Header (Centered)
            title_surf = self.font_large.render("GAME PAUSED", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(disp_width // 2, (disp_height // 2) - 130))
            surface.blit(title_surf, title_rect)

            # Current Score Display (Centered)
            score_text = f"CURRENT SCORE: {int(current_score)}"
            score_surf = self.font_medium.render(score_text, True, (220, 220, 220))
            score_rect = score_surf.get_rect(center=(disp_width // 2, (disp_height // 2) - 70))
            surface.blit(score_surf, score_rect)

            # Draw Menu Buttons
            self.resume_btn.draw(surface, self.font_small)
            self.restart_btn.draw(surface, self.font_small)
            self.quit_btn.draw(surface, self.font_small)

            pygame.display.flip()
            clock.tick(60)

        # Smooth Countdown on Resume
        if action == "RESUME":
            countdown_steps = ["3", "2", "1", "START!"]
            for step in countdown_steps:
                start_ticks = pygame.time.get_ticks()
                while pygame.time.get_ticks() - start_ticks < 1000:
                    surface.blit(scaled_snapshot, (0, 0))

                    overlay = pygame.Surface((disp_width, disp_height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 150))
                    surface.blit(overlay, (0, 0))

                    count_surf = self.font_countdown.render(step, True, (255, 50, 50))
                    count_rect = count_surf.get_rect(center=(disp_width // 2, (disp_height // 2) - 20))
                    surface.blit(count_surf, count_rect)

                    pygame.display.flip()
                    clock.tick(60)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

        return action