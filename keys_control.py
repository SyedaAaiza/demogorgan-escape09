import pygame


class KeysController:
    def __init__(self):
        # 1. PERMEANT LANE X-POSITIONS
        # main.py के LANE_RATIOS (0.16, 0.475, 0.80) के साथ 800px विड्थ पर 100% एलाइंड
        self.lanes = [128, 345, 555]
        self.current_lane = 1  # Start in Center Lane

        # 2. FAST LANE TRANSITION SPEED
        # साइड लेन्स में तुरंत शिफ्ट करने के लिए स्पीड बढ़ा दी गई है
        self.lane_transition_speed = 45

        # 3. BALANCED FAST JUMP & GRAVITY PHYSICS
        self.is_jumping = False
        self.jump_count = 0
        self.max_jumps = 2

        # -22 और -20 से जंप तेज होगी पर स्क्रीन से बाहर नहीं जाएगी
        self.jump_velocity = -35
        self.double_jump_velocity = -20

        # High gravity ताकि जंप क्विक और रिस्पॉन्सिव रहे (लटकने वाली न लगे)
        self.gravity = 1.6
        self.y_velocity = 0

        # Crouch state
        self.is_crouching = False

    def update(self, char_x, char_y, ground_y, facing_right, events):
        keys = pygame.key.get_pressed()

        # Hold to Crouch (Down Arrow, 's', or Left Shift)
        down_held = keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_LSHIFT]
        if down_held and not self.is_jumping:
            self.is_crouching = True
        else:
            self.is_crouching = False

        # Key press events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.current_lane > 0:
                    self.current_lane -= 1
                    facing_right = False
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.current_lane < 2:
                    self.current_lane += 1
                    facing_right = True
                elif (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not self.is_crouching:
                    if not self.is_jumping:
                        self.is_jumping = True
                        self.jump_count = 1
                        self.y_velocity = self.jump_velocity
                    elif self.jump_count < self.max_jumps:
                        self.jump_count += 1
                        self.y_velocity = self.double_jump_velocity

        # Smooth and Instant Lane Slide
        target_x = self.lanes[self.current_lane]
        if char_x < target_x:
            char_x = min(target_x, char_x + self.lane_transition_speed)
        elif char_x > target_x:
            char_x = max(target_x, char_x - self.lane_transition_speed)

        # Independent Jump Physics (Works identically in ALL lanes)
        if self.is_jumping:
            char_y += self.y_velocity
            self.y_velocity += self.gravity

            if char_y >= ground_y:
                char_y = ground_y
                self.is_jumping = False
                self.jump_count = 0
                self.y_velocity = 0

        return char_x, char_y, facing_right, self.is_jumping, self.is_crouching, self.jump_count