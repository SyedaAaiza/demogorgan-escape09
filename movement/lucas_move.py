import os
import pygame
from keys_control import KeysController


class PlayerRunner:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.ground_y = 420
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "..", "assets")
        self.sprites_right = []
        self.sprites_left = []

        # Will, Mike, aur Max ke jaisa exact size aur dimensions
        self.char_w = 170
        self.char_h = 170

        for i in range(1, 6):
            img = None
            for ext in [".png", ".PNG", ".jpeg", ".JPEG", ".jpg", ".JPG"]:
                path = os.path.join(assets_dir, f"lucas{i}{ext}")
                if os.path.exists(path):
                    try:
                        raw = pygame.image.load(path).convert_alpha()
                        img = pygame.transform.smoothscale(raw, (self.char_w, self.char_h))
                        break
                    except Exception as e:
                        print(f"Error loading {path}: {e}")

            # Fallback agar lucas1.png waghera na milein
            if img is None:
                surf = pygame.Surface((self.char_w, self.char_h), pygame.SRCALPHA)
                surf.fill((46, 139, 87, 200))  # Greenish box agar image missing ho
                img = surf

            self.sprites_right.append(img)
            self.sprites_left.append(pygame.transform.flip(img, True, False))

        self.controller = KeysController()
        self.char_x = self.controller.lanes[1]
        self.char_y = self.ground_y
        self.facing_right = True
        self.current_frame = 0.0
        self.anim_speed = 0.25
        self.image = self.sprites_right[0]
        self.x = self.char_x
        self.y = self.char_y

    def update(self, events):
        (self.char_x, self.char_y, self.facing_right, self.is_jumping, self.is_rolling,
         self.jump_count,) = self.controller.update(self.char_x, self.char_y, self.ground_y, self.facing_right, events)
        self.current_frame = (self.current_frame + self.anim_speed) % len(self.sprites_right)

    def draw(self, surface):
        active_set = self.sprites_right if self.facing_right else self.sprites_left
        render_image = active_set[int(self.current_frame)]
        if self.is_rolling:
            render_image = pygame.transform.scale(render_image, (self.char_w, self.char_h // 2))
        draw_y = self.char_y if not self.is_rolling else self.char_y + 60
        self.image = render_image
        self.x = self.char_x
        self.y = draw_y
        surface.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.char_w, (self.char_h // 2) if self.is_rolling else self.char_h)