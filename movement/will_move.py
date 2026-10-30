import os
import pygame
from PIL import Image
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
        for i in range(1, 6):
            path = os.path.join(assets_dir, f"will{i}.jpeg")
            cleaned_img = self.clean_jpeg_background(path, target_size=(130, 130))
            self.sprites_right.append(cleaned_img)
            self.sprites_left.append(pygame.transform.flip(cleaned_img, True, False))
        self.controller = KeysController()
        self.char_x = self.controller.lanes[1]
        self.char_y = self.ground_y
        self.facing_right = True
        self.current_frame = 0.0
        self.anim_speed = 0.25
        self.image = self.sprites_right[0]
        self.x = self.char_x
        self.y = self.char_y

    def clean_jpeg_background(self, image_path, target_size=(130, 130)):
        if not os.path.exists(image_path):
            surf = pygame.Surface(target_size, pygame.SRCALPHA)
            surf.fill((255, 0, 0, 0))
            return surf
        pil_img = Image.open(image_path).convert("RGBA")
        data = pil_img.getdata()
        new_data = []
        for item in data:
            r, g, b, a = item
            if r > 210 and g > 210 and b > 210:
                avg = (r + g + b) // 3
                alpha = max(0, 255 - int((avg - 210) * (255 / 45)))
                new_data.append((r, g, b, alpha))
            else:
                new_data.append((r, g, b, 255))
        pil_img.putdata(new_data)
        raw_str = pil_img.tobytes()
        pygame_img = pygame.image.fromstring(raw_str, pil_img.size, "RGBA")
        return pygame.transform.smoothscale(pygame_img, target_size)

    def update(self, events):
        (self.char_x, self.char_y, self.facing_right, self.is_jumping, self.is_rolling, self.jump_count,) = self.controller.update(self.char_x, self.char_y, self.ground_y, self.facing_right, events)
        self.current_frame = (self.current_frame + self.anim_speed) % len(self.sprites_right)

    def draw(self, surface):
        active_set = self.sprites_right if self.facing_right else self.sprites_left
        render_image = active_set[int(self.current_frame)]
        if self.is_rolling:
            render_image = pygame.transform.scale(render_image, (130, 70))
        draw_y = self.char_y if not self.is_rolling else self.char_y + 60
        self.image = render_image
        self.x = self.char_x
        self.y = draw_y
        surface.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 130, 70 if self.is_rolling else 130)