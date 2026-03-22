import pygame

from player import Player
from utils import IMAGES, SOUNDS, FONTS, SCREEN_WIDTH, SCREEN_HEIGHT, TOP_UI_LAYER_HEIGHT


def draw_hud_button(screen, rect, label, font, hovered=False, active=False, accent="blue"):
    shadow_rect = rect.move(0, 2)
    shadow_color = (3, 16, 24)
    if accent == "coral":
        base_color = (196, 103, 77) if not hovered else (225, 125, 96)
        if active:
            base_color = (206, 137, 60)
        border_color = (255, 230, 194) if hovered else (255, 206, 166)
    else:
        base_color = (24, 95, 122) if not hovered else (36, 126, 157)
        if active:
            base_color = (19, 129, 102)
        border_color = (168, 233, 241) if hovered else (120, 199, 214)
    highlight_color = (255, 255, 255)

    shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, shadow_color, shadow_surface.get_rect(), border_radius=14)
    screen.blit(shadow_surface, shadow_rect.topleft)

    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(button_surface, base_color, button_surface.get_rect(), border_radius=14)
    pygame.draw.rect(button_surface, border_color, button_surface.get_rect(), width=2, border_radius=14)

    gloss_rect = pygame.Rect(4, 4, rect.width - 8, max(8, rect.height // 4))
    gloss_surface = pygame.Surface((gloss_rect.width, gloss_rect.height), pygame.SRCALPHA)
    gloss_surface.fill(base_color)
    gloss_surface.set_alpha(18)
    pygame.draw.rect(gloss_surface, highlight_color, gloss_surface.get_rect(), border_radius=10)
    button_surface.blit(gloss_surface, gloss_rect.topleft)

    text_color = (232, 249, 252)
    text_surface = font.render(label, True, text_color)
    text_rect = text_surface.get_rect(center=(rect.width // 2, rect.height // 2 - 1))
    button_surface.blit(text_surface, text_rect)
    screen.blit(button_surface, rect.topleft)


def draw_mask(surface, mask, x, y, color=(255, 0, 0)):
    if mask:
        mask_surface = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
        surface.blit(mask_surface, (x, y))


def render_start_screen(screen, start_screen_bg, start_button_rect, high_score_enabled, high_score):
    if start_screen_bg:
        screen.blit(start_screen_bg, (0, 0))
    else:
        screen.fill((0, 0, 0))

    mouse_position = pygame.mouse.get_pos()
    draw_hud_button(
        screen,
        start_button_rect,
        "Click to Start",
        FONTS["ocean_font_22"],
        hovered=start_button_rect.collidepoint(mouse_position),
        accent="coral",
    )

    if high_score_enabled:
        high_score_text = FONTS["ocean_font_22"].render(
            "High Score: " + str(high_score), True, (255, 255, 255)
        )
        high_score_rect = high_score_text.get_rect(center=((SCREEN_WIDTH // 2) - 14, 250))
        screen.blit(high_score_text, high_score_rect)


def render_info_screen(screen, info_screen_bg):
    if info_screen_bg:
        screen.blit(info_screen_bg, (0, 0))
    else:
        screen.fill((0, 0, 0))


def render_game_over_screen(screen, score, high_score_enabled, high_score, is_new_high_score):
    screen.fill((0, 0, 0))
    title_text = FONTS["ocean_font_48"].render("Game Over", True, (255, 255, 255))
    restart_text = FONTS["ocean_font_22"].render("Click to restart", True, (255, 255, 255))
    points_text = FONTS["ocean_font_22"].render("Points: " + str(score), True, (255, 255, 255))
    screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
    screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)))
    screen.blit(points_text, points_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))

    if high_score_enabled:
        high_score_text = FONTS["ocean_font_22"].render(
            "High Score: " + str(high_score), True, (255, 255, 255)
        )
        screen.blit(high_score_text, high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)))

        if is_new_high_score:
            new_record_text = FONTS["ocean_font_22"].render("New High Score!", True, (255, 214, 140))
            screen.blit(new_record_text, new_record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130)))


def render_play_screen(screen, zoomed_surface, game_state_manager, camera_x, camera_y, y_first, y_second, debug=False):
    world_height = SCREEN_HEIGHT

    zoomed_surface.fill((0, 0, 0))
    zoomed_surface.blit(IMAGES["play_background"], (-camera_x, y_first - camera_y))
    zoomed_surface.blit(IMAGES["play_background"], (-camera_x, y_second - camera_y))

    if camera_y > world_height - SCREEN_HEIGHT - 100:
        zoomed_surface.blit(IMAGES["ground"], (-camera_x, world_height - 100 - camera_y))

    for sprite in game_state_manager.allsprites:
        zoomed_surface.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y))

    for arrow_sprite in game_state_manager.arrow_warning_sprites:
        arrow_sprite.update()
        if arrow_sprite.visible:
            zoomed_surface.blit(
                arrow_sprite.image,
                (arrow_sprite.rect.x - camera_x, arrow_sprite.rect.y - camera_y),
            )

    if debug:
        draw_mask(
            zoomed_surface,
            game_state_manager.player.body_mask,
            game_state_manager.player.rect.x - camera_x,
            game_state_manager.player.rect.y - camera_y,
            (63, 26, 186),
        )
        draw_mask(
            zoomed_surface,
            game_state_manager.player.face_mask,
            game_state_manager.player.rect.x - camera_x,
            game_state_manager.player.rect.y - camera_y,
        )
        draw_mask(
            zoomed_surface,
            game_state_manager.rainbow_fish.body_mask,
            game_state_manager.rainbow_fish.rect.x - camera_x,
            game_state_manager.rainbow_fish.rect.y - camera_y,
            (0, 128, 0),
        )
        draw_mask(
            zoomed_surface,
            game_state_manager.rainbow_fish.face_mask,
            game_state_manager.rainbow_fish.rect.x - camera_x,
            game_state_manager.rainbow_fish.rect.y - camera_y,
        )

    if game_state_manager.score_blit > 0:
        relative_x = game_state_manager.dead_fish_position[0] - camera_x
        relative_y = game_state_manager.dead_fish_position[1] - camera_y
        score_blit_text = FONTS["ocean_font_16"].render(
            "+" + str(game_state_manager.score_blit), True, (255, 255, 255)
        )
        zoomed_surface.blit(score_blit_text, (relative_x, relative_y))
        game_state_manager.score_disappear_timer += 1

        if game_state_manager.score_disappear_timer > game_state_manager.SCORE_BLIT_TICKS_TO_DISAPPEAR:
            game_state_manager.score_blit = 0
            game_state_manager.score_disappear_timer = 0

    scaled_zoomed_area = pygame.transform.scale(zoomed_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_zoomed_area, (0, 0))


def render_ui_overlay(screen, game_state_manager, pause_button_rect, joystick):
    if game_state_manager.joystick_visible:
        joystick.draw(game_state_manager.key_states, game_state_manager.touch_position)
        pygame.draw.circle(screen, (255, 0, 0), game_state_manager.touch_position, 5)

    screen.blit(IMAGES["top_ui_layer"], (0, 0))
    available_prey_text = FONTS["ocean_font_22"].render("Available Prey:", True, (255, 255, 255))
    text_rect = available_prey_text.get_rect(topleft=(10, TOP_UI_LAYER_HEIGHT / 2 - 10))
    screen.blit(available_prey_text, text_rect)

    mouse_position = pygame.mouse.get_pos()
    pause_or_resume_text = "Resume" if game_state_manager.is_paused else "Pause"
    draw_hud_button(
        screen,
        pause_button_rect,
        pause_or_resume_text,
        FONTS["ocean_font_16"],
        hovered=pause_button_rect.collidepoint(mouse_position),
        active=game_state_manager.is_paused,
    )

    draw_hud_button(
        screen,
        game_state_manager.info_button_play_rect,
        "Info",
        FONTS["ocean_font_16"],
        hovered=game_state_manager.info_button_play_rect.collidepoint(mouse_position),
    )

    icon_x = text_rect.right + 10
    base_icon_y = TOP_UI_LAYER_HEIGHT / 2 - 3
    icon_buffer = 10
    standard_icons = ["spr_red_fish", "spr_green_fish_left", "spr_silver_fish"]
    max_height_standard = max(IMAGES[key].get_height() for key in standard_icons)

    for icon_key in standard_icons:
        icon = IMAGES[icon_key]
        icon_y = base_icon_y + (max_height_standard - icon.get_height()) // 2
        screen.blit(icon, (icon_x, icon_y))
        icon_x += icon.get_width() + icon_buffer

    scaled_icon_size = (24, 15)
    scaled_icons = []

    if game_state_manager.rainbow_fish.size_score <= game_state_manager.player.size_score:
        scaled_icons.append(pygame.transform.smoothscale(IMAGES["spr_rainbow_fish_left"], scaled_icon_size))
    if game_state_manager.player.size_score >= Player.PLAYER_SCORE_BIGGER_THAN_BIG_GREEN_FISH:
        scaled_icons.append(pygame.transform.smoothscale(IMAGES["spr_big_green_fish_left"], scaled_icon_size))
    if game_state_manager.player.star_power == Player.SHARK_SHRINKER_POWERUP:
        scaled_icons.append(pygame.transform.smoothscale(IMAGES["spr_shark_left"], scaled_icon_size))

    for icon in scaled_icons:
        vertical_offset = (max_height_standard - icon.get_height()) // 2
        icon_y = base_icon_y + vertical_offset
        screen.blit(icon, (icon_x, icon_y))
        icon_x += icon.get_width() + icon_buffer

    score_text = FONTS["ocean_font_22"].render("Score: " + str(game_state_manager.score), 1, (255, 255, 255))
    screen.blit(score_text, ((SCREEN_WIDTH / 2) - 50, TOP_UI_LAYER_HEIGHT / 2 - 10))

    screen.blit(
        game_state_manager.player.get_powerup_timer_text(FONTS["ocean_font_16"]),
        (SCREEN_WIDTH * 0.68, TOP_UI_LAYER_HEIGHT / 2 - 7),
    )
    screen.blit(
        game_state_manager.player.get_speed_timer_text(FONTS["ocean_font_16"]),
        (SCREEN_WIDTH * 0.56, TOP_UI_LAYER_HEIGHT / 2 - 7),
    )

    if game_state_manager.player.star_power == Player.NO_STAR_POWER:
        game_state_manager.one_powerup_sound -= 1
        SOUNDS["snd_powerup_timer"].stop()
    if game_state_manager.player.speed_time_left < 0:
        game_state_manager.one_powerup_sound -= 1
        SOUNDS["snd_powerup_timer"].stop()
