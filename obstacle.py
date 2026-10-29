import os
import random
import pygame


class ObstacleManager:

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_interval = 1300
        self.HORIZON_Y = 320
        self.lane_positions = []

        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")
        self.obstacle_images = []
        for i in range(1, 10):
            img_path = os.path.join(assets_dir, f"obs{i}.png")
            if not os.path.exists(img_path):
                img_path = os.path.join(assets_dir, f"obs{i}.jpeg")
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    self.obstacle_images.append(img)
                except:
                    pass

    def update_and_spawn(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            lane_idx = random.randint(0, 2)
            chosen = (
                random.choice(self.obstacle_images)
                if self.obstacle_images
                else None
            )
            self.obstacles.append({
                "lane_idx": lane_idx,
                "z": 1.0,  # 1.0 = Far at Horizon, 0.0 = Player Feet Level
                "base_w": 110,
                "base_h": 160,
                "speed": 0.0008,  # Properly calibrated depth speed
                "image": chosen,
            })

        for obs in self.obstacles[:]:
            # Z decreases as obstacle moves closer to screen bottom
            obs["z"] -= obs["speed"] * dt
            progress = max(0.0, 1.0 - obs["z"])

            # Curve Y position down the track
            obs["y"] = self.HORIZON_Y + (self.height - self.HORIZON_Y) * (
                progress**2
            )

            # Scale size with pseudo-3D perspective depth
            scale = 0.35 + (progress * 0.95)
            obs["width"] = int(obs["base_w"] * scale)
            obs["height"] = int(obs["base_h"] * scale)

            # Calculate X position along perspective track lanes
            if self.lane_positions:
                lane = self.lane_positions[obs["lane_idx"]]
                obs["current_x"] = lane["top_x"] + (
                    lane["bottom_x"] - lane["top_x"]
                ) * progress
            else:
                obs["current_x"] = self.width // 2

            # Pre-generate pixel mask for active scaled surface
            if obs.get("image"):
                scaled_surface = pygame.transform.smoothscale(
                    obs["image"], (obs["width"], obs["height"])
                )
                obs["scaled_surface"] = scaled_surface
                obs["mask"] = pygame.mask.from_surface(scaled_surface)

            # Remove obstacle after passing far past player
            if obs["z"] <= -0.2:
                self.obstacles.remove(obs)

    def draw(self, screen):
        for obs in sorted(self.obstacles, key=lambda o: o["y"]):
            x = obs.get("current_x", 0)
            if obs.get("scaled_surface"):
                screen.blit(
                    obs["scaled_surface"], (x - obs["width"] // 2, obs["y"])
                )

    def check_collision(self, player):
        """Precise Pseudo-3D Depth and Sprite Mask Collision Check."""
        if not hasattr(player, "image") or player.image is None:
            return False

        player_x = getattr(player, "x", getattr(player, "char_x", 0))
        player_y = getattr(player, "y", getattr(player, "char_y", 0))

        # Core player sprite dimensions
        player_w = player.image.get_width()
        player_h = player.image.get_height()

        for obs in self.obstacles:
            # 1. DEPTH GATE: Only check collision when obstacle reaches player's depth plane (Z <= 0.35)
            if obs.get("z", 1.0) > 0.35:
                continue

            obs_x = obs.get("current_x", 0) - obs["width"] // 2
            obs_y = obs["y"]

            # Offset between top-left of player sprite and obstacle sprite
            offset_x = int(obs_x - player_x)
            offset_y = int(obs_y - player_y)

            # 2. PIXEL-PERFECT MASK OVERLAP
            player_mask = pygame.mask.from_surface(player.image)
            obs_mask = obs.get("mask")

            if obs_mask:
                overlap_point = player_mask.overlap(obs_mask, (offset_x, offset_y))
                if overlap_point:
                    print(f"COLLISION CONFIRMED at pixel point: {overlap_point}")
                    return True
            else:
                # Fallback bounding box check
                p_rect = pygame.Rect(player_x + 15, player_y + 15, player_w - 30, player_h - 30)
                o_rect = pygame.Rect(obs_x + 10, obs_y + 10, obs["width"] - 20, obs["height"] - 20)
                if p_rect.colliderect(o_rect):
                    return True

        return False

    def get_player_lane_from_screen(self, screen_lanes, player_screen_x):
        if not screen_lanes or len(screen_lanes) < 3:
            return 1
        left_mid = (
            screen_lanes[0]["bottom_x"] + screen_lanes[1]["bottom_x"]
        ) // 2
        right_mid = (
            screen_lanes[1]["bottom_x"] + screen_lanes[2]["bottom_x"]
        ) // 2

        if player_screen_x < left_mid:
            return 0
        elif player_screen_x < right_mid:
            return 1
        else:
            return 2