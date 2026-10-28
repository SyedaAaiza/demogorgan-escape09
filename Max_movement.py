import pygame
import sys

# 1. Initialize Pygame
pygame.init()

# 2. Screen Settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Surfers Style 3-Lane Runner with 4-Frame Roll")

clock = pygame.time.Clock()

# 3. Load Character Running Animation Frames (max1 to max5)
walk_frames = []
for i in range(1, 6):
    try:
        frame = pygame.image.load(f"max{i}.png").convert_alpha()
        frame = pygame.transform.scale(frame, (200, 200))
        walk_frames.append(frame)
    except FileNotFoundError:
        print(f"Warning: Could not find 'max{i}.png'.")

# 4. Load Character Rolling Animation Frames (maxroll1 to maxroll4)
roll_frames = []
for i in range(1, 5):  # Adjusted to load 4 frames (maxroll1 to maxroll4)
    try:
        frame = pygame.image.load(f"maxroll{i}.png").convert_alpha()
        frame = pygame.transform.scale(frame, (180, 110))
        roll_frames.append(frame)
    except FileNotFoundError:
        print(f"Warning: Could not find 'maxroll{i}.png'. Make sure it's in your project folder.")

# Animation variables
current_frame = 0
animation_speed = 0.2  # Speed of the running cycle
roll_frame_index = 0
roll_anim_speed = 0.3  # Speed of the rolling animation cycle

# Lane settings (3-Lane Subway Surfers style)
lanes = [250, 400, 550]  # X coordinates for Left, Middle, and Right lanes
current_lane = 1  # Start in the middle lane (index 1)
player_x = lanes[current_lane]

# Ground & Jump Physics variables
base_ground_y = 450  # Fixed floor level height
jump_y_offset = 0  # Vertical position offset during a jump
jump_velocity = 0
gravity = 0.8
jump_strength = -14  # Initial upward push power
is_jumping = False

# Roll variables
is_rolling = False
roll_timer = 0
roll_duration = 35  # How many frames the roll lasts before standing back up

# Main Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # Lane switching (Left/Right or A/D)
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if current_lane > 0:
                    current_lane -= 1
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if current_lane < len(lanes) - 1:
                    current_lane += 1

            # Jump trigger (Spacebar, Up Arrow, or W) - only if not rolling or jumping
            if (
                    event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w) and not is_jumping and not is_rolling:
                is_jumping = True
                jump_velocity = jump_strength

            # Roll trigger (Down Arrow or S) - only if not already rolling or jumping
            if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and not is_rolling and not is_jumping:
                is_rolling = True
                roll_timer = roll_duration
                roll_frame_index = 0  # Reset roll animation to start

    # Handle Jump Physics
    if is_jumping:
        jump_velocity += gravity  # Pulls the character down over time
        jump_y_offset += jump_velocity  # Updates vertical height

        # Land back on the ground when offset returns to 0
        if jump_y_offset >= 0:
            jump_y_offset = 0
            is_jumping = False
            jump_velocity = 0

    # Handle Roll Timer & State
    if is_rolling:
        roll_timer -= 1
        if roll_timer <= 0:
            is_rolling = False

    # Smoothly slide player towards the target lane position
    target_x = lanes[current_lane]
    player_x += (target_x - player_x) * 0.2

    # Update animation frame indices smoothly
    if is_rolling and roll_frames:
        roll_frame_index += roll_anim_speed
        if roll_frame_index >= len(roll_frames):
            roll_frame_index = 0  # Loop roll frames
    elif walk_frames:
        current_frame += animation_speed
        if current_frame >= len(walk_frames):
            current_frame = 0  # Loop run frames

    # Drawing / Rendering
    screen.fill((100, 149, 237))  # Sky blue background

    # Draw faint lane lines for reference
    for lane_x in lanes:
        pygame.draw.line(screen, (150, 180, 240), (lane_x + 50, 0), (lane_x + 50, HEIGHT), 3)

    # Draw ground line (fixed at base_ground_y)
    pygame.draw.line(screen, (46, 139, 87), (0, base_ground_y), (WIDTH, base_ground_y), 5)

    # Select the correct sprite sheet frames based on player state
    if is_rolling and roll_frames:
        active_image = roll_frames[int(roll_frame_index)]
    elif walk_frames:
        active_image = walk_frames[int(current_frame)]
    else:
        active_image = None

    # Draw the active frame centered on the lane and anchored to the ground
    if active_image:
        image_width = active_image.get_width()
        image_height = active_image.get_height()

        render_x = player_x - image_width // 2
        render_y = base_ground_y - image_height + jump_y_offset

        screen.blit(active_image, (render_x, render_y))

    pygame.display.flip()
    clock.tick(60)