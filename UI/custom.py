import os
import pygame
import sys
import json

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Demogorgan Escape - Character & Player Setup")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(BASE_DIR).lower() == "ui":
    parent_dir = os.path.dirname(BASE_DIR)
    current_dir = BASE_DIR
else:
    parent_dir = BASE_DIR
    current_dir = os.path.join(BASE_DIR, "UI")

assets_dir = os.path.join(parent_dir, "assets")
os.makedirs(current_dir, exist_ok=True)

characters = [
    {"name": "WILL", "file_base": "will", "color": (70, 130, 180)},
    {"name": "MIKE", "file_base": "mike", "color": (220, 20, 60)},
    {"name": "DUSTIN", "file_base": "dustin", "color": (255, 215, 0)},
    {"name": "LUCAS", "file_base": "lucas", "color": (46, 139, 87)},
    {"name": "MAX", "file_base": "max", "color": (255, 140, 0)},
    {"name": "ELEVEN", "file_base": "el", "color": (147, 112, 219)}
]
selected_index = 1

for char in characters:
    img = None
    for ext in [".png", ".PNG", ".jpeg", ".JPEG", ".jpg", ".JPG"]:
        test_path = os.path.join(assets_dir, char["file_base"] + ext)
        if os.path.exists(test_path):
            try:
                img = pygame.image.load(test_path).convert_alpha()
                break
            except Exception as e:
                print(f"Error loading {test_path}: {e}")
    if img:
        if char["name"] == "MIKE":
            char["image"] = pygame.transform.smoothscale(img, (200, 160))
        else:
            char["image"] = pygame.transform.smoothscale(img, (95, 140))
    else:
        char["image"] = None

bg_image = None
for ext in [".png", ".PNG", ".jpeg", ".JPEG", ".jpg", ".JPG"]:
    bg_path = os.path.join(assets_dir, "bgchar" + ext)
    if os.path.exists(bg_path):
        try:
            bg_image = pygame.image.load(bg_path).convert()
            bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
            break
        except Exception:
            pass

font_path = os.path.join(assets_dir, "BebasNeue-Regular.ttf")
try:
    font_title = pygame.font.Font(font_path, 52)
    font_name = pygame.font.Font(font_path, 26)
    font_instruction = pygame.font.Font(font_path, 22)
except Exception:
    font_title = pygame.font.SysFont("Impact", 52)
    font_name = pygame.font.SysFont("Impact", 26)
    font_instruction = pygame.font.SysFont("Arial", 22)

BORDER_COLOR = (255, 204, 0)
TEXT_COLOR = (255, 255, 255)

game_state = "SELECT"
chosen_character = characters[selected_index]["name"]
player_name = chosen_character

name_btn_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT - 150, 320, 50)
save_btn_rect = pygame.Rect(0, 0, 0, 0)

def save_to_json(char, name):
    data = {"selected_character": char, "player_name": name}
    json_path = os.path.join(current_dir, "player_data.json")
    try:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved to {json_path}: {data}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

while True:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_state == "SELECT":
                    if name_btn_rect.collidepoint(event.pos):
                        chosen_character = characters[selected_index]["name"]
                        player_name = chosen_character
                        game_state = "ENTER_NAME"
                elif game_state == "ENTER_NAME":
                    if save_btn_rect.collidepoint(event.pos):
                        if player_name.strip() == "":
                            player_name = chosen_character
                        save_to_json(chosen_character, player_name)
                        game_state = "PLAYING"
        if event.type == pygame.KEYDOWN:
            if game_state == "SELECT":
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    selected_index = (selected_index - 1) % len(characters)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    selected_index = (selected_index + 1) % len(characters)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    chosen_character = characters[selected_index]["name"]
                    player_name = chosen_character
                    game_state = "ENTER_NAME"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif game_state == "ENTER_NAME":
                if event.key == pygame.K_RETURN:
                    if player_name.strip() == "":
                        player_name = chosen_character
                    save_to_json(chosen_character, player_name)
                    game_state = "PLAYING"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    game_state = "SELECT"
                else:
                    if len(player_name) < 15 and event.unicode.isprintable():
                        if player_name == chosen_character:
                            player_name = ""
                        player_name += event.unicode
            elif game_state == "PLAYING":
                if event.key == pygame.K_ESCAPE:
                    game_state = "SELECT"

    if bg_image:
        screen.blit(bg_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill((24, 43, 73))

    if game_state == "SELECT":
        header_rect = pygame.Rect(0, 40, WIDTH, 80)
        pygame.draw.rect(screen, (0, 0, 0), header_rect)
        title_surf = font_title.render("SELECT YOUR RUNNER", True, BORDER_COLOR)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 58))
        card_width, card_height = 110, 240
        spacing = 15
        total_width = (len(characters) * card_width) + ((len(characters) - 1) * spacing)
        start_x = (WIDTH - total_width) // 2
        y_pos = HEIGHT // 2 - 120
        for i, char in enumerate(characters):
            x_pos = start_x + (i * (card_width + spacing))
            is_selected = (i == selected_index)
            current_card_height = card_height + 15 if is_selected else card_height
            current_y = y_pos - 15 if is_selected else y_pos
            card_rect = pygame.Rect(x_pos, current_y, card_width, current_card_height)
            pygame.draw.rect(screen, (40, 70, 110), card_rect, border_radius=15)
            portrait_rect = pygame.Rect(x_pos + 10, current_y + 10, card_width - 20, current_card_height - 65)
            pygame.draw.rect(screen, char["color"], portrait_rect, border_radius=10)
            if char["image"]:
                img_x = portrait_rect.centerx - char["image"].get_width() // 2
                img_y = portrait_rect.centery - char["image"].get_height() // 2
                screen.blit(char["image"], (img_x, img_y))
            if is_selected:
                pygame.draw.rect(screen, BORDER_COLOR, card_rect, 5, border_radius=15)
            else:
                pygame.draw.rect(screen, (70, 100, 140), card_rect, 2, border_radius=15)
            name_surf = font_name.render(char["name"], True, TEXT_COLOR)
            name_x = x_pos + (card_width // 2) - (name_surf.get_width() // 2)
            name_y = current_y + current_card_height - 42
            screen.blit(name_surf, (name_x, name_y))
        btn_hovered = name_btn_rect.collidepoint(mouse_pos)
        btn_bg_color = (230, 180, 0) if btn_hovered else BORDER_COLOR
        pygame.draw.rect(screen, btn_bg_color, name_btn_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), name_btn_rect, 2, border_radius=12)
        btn_text = font_name.render("CLICK TO ENTER NAME", True, (0, 0, 0))
        screen.blit(btn_text, (name_btn_rect.centerx - btn_text.get_width() // 2, name_btn_rect.centery - btn_text.get_height() // 2))
        inst_bg = pygame.Rect(0, HEIGHT - 70, WIDTH, 60)
        pygame.draw.rect(screen, (0, 0, 0), inst_bg)
        inst_surf = font_instruction.render("◀ ▶ Select Character | Click Button or Press [ENTER] | [ESC] Exit", True, TEXT_COLOR)
        screen.blit(inst_surf, (WIDTH // 2 - inst_surf.get_width() // 2, HEIGHT - 50))
    elif game_state == "ENTER_NAME":
        box_width, box_height = 520, 260
        box_x = WIDTH // 2 - box_width // 2
        box_y = HEIGHT // 2 - box_height // 2
        input_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (15, 28, 48), input_box_rect, border_radius=20)
        pygame.draw.rect(screen, BORDER_COLOR, input_box_rect, 4, border_radius=20)
        prompt_surf = font_name.render("ENTER YOUR PLAYER NAME:", True, TEXT_COLOR)
        screen.blit(prompt_surf, (box_x + box_width // 2 - prompt_surf.get_width() // 2, box_y + 25))
        text_field_rect = pygame.Rect(box_x + 40, box_y + 75, box_width - 80, 45)
        pygame.draw.rect(screen, (255, 255, 255), text_field_rect, border_radius=10)
        name_surf = font_name.render(player_name + "|", True, (0, 0, 0))
        screen.blit(name_surf, (text_field_rect.x + 15, text_field_rect.y + 8))
        save_btn_rect = pygame.Rect(box_x + 110, box_y + 140, box_width - 220, 45)
        save_hovered = save_btn_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (46, 139, 87) if save_hovered else (34, 102, 64), save_btn_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), save_btn_rect, 2, border_radius=10)
        save_txt = font_name.render("SAVE & START GAME", True, TEXT_COLOR)
        screen.blit(save_txt, (save_btn_rect.centerx - save_txt.get_width() // 2, save_btn_rect.centery - save_txt.get_height() // 2))
        sub_inst = font_instruction.render("[BACKSPACE] Delete | [ESC] Back to Selection", True, (200, 200, 200))
        screen.blit(sub_inst, (box_x + box_width // 2 - sub_inst.get_width() // 2, box_y + 205))
    elif game_state == "PLAYING":
        play_surf = font_title.render(f"Runner: {chosen_character}", True, BORDER_COLOR)
        screen.blit(play_surf, (WIDTH // 2 - play_surf.get_width() // 2, HEIGHT // 2 - 60))
        name_display = font_name.render(f"Player Name: {player_name}", True, TEXT_COLOR)
        screen.blit(name_display, (WIDTH // 2 - name_display.get_width() // 2, HEIGHT // 2 + 10))
        back_surf = font_instruction.render("Press [ESC] to go back to selection", True, (180, 180, 180))
        screen.blit(back_surf, (WIDTH // 2 - back_surf.get_width() // 2, HEIGHT // 2 + 70))

    pygame.display.flip()
    clock.tick(60)