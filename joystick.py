import math

import pygame

from utils import SCREEN_HEIGHT


class Joystick:
    def __init__(self, images, screen):
        self.images = images
        self.screen = screen
        self.pressed_direction = None
        self.neutral_zone_rect = images["spr_neutral_zone"].get_rect(center=(158, SCREEN_HEIGHT - 143))
        self.arrows = {
            "up_left": self.images["spr_unpressed_arrow_up_left"].get_rect(topleft=(20, SCREEN_HEIGHT - 280)),
            "up_right": self.images["spr_unpressed_arrow_up_right"].get_rect(topleft=(200, SCREEN_HEIGHT - 280)),
            "down_left": self.images["spr_unpressed_arrow_down_left"].get_rect(topleft=(20, SCREEN_HEIGHT - 100)),
            "down_right": self.images["spr_unpressed_arrow_down_right"].get_rect(topleft=(200, SCREEN_HEIGHT - 100)),
            "up": self.images["spr_unpressed_arrow_up"].get_rect(topleft=(110, SCREEN_HEIGHT - 280)),
            "down": self.images["spr_unpressed_arrow_down"].get_rect(topleft=(110, SCREEN_HEIGHT - 100)),
            "left": self.images["spr_unpressed_arrow_left"].get_rect(topleft=(20, SCREEN_HEIGHT - 190)),
            "right": self.images["spr_unpressed_arrow_right"].get_rect(topleft=(200, SCREEN_HEIGHT - 190)),
        }
        self.key_to_direction = {
            (pygame.K_UP,): "up",
            (pygame.K_DOWN,): "down",
            (pygame.K_LEFT,): "left",
            (pygame.K_RIGHT,): "right",
            (pygame.K_UP, pygame.K_RIGHT): "up_right",
            (pygame.K_UP, pygame.K_LEFT): "up_left",
            (pygame.K_DOWN, pygame.K_RIGHT): "down_right",
            (pygame.K_DOWN, pygame.K_LEFT): "down_left",
        }
        self.mouse_is_pressed = False
        self.activation_distance = 30
        self.center_position = None

    def draw(self, key_states, center_position):
        if center_position is None:
            return

        neutral_zone_size = self.images["spr_neutral_zone"].get_size()
        neutral_zone_top_left = (
            center_position[0] - neutral_zone_size[0] // 2,
            center_position[1] - neutral_zone_size[1] // 2,
        )
        self.screen.blit(self.images["spr_neutral_zone"], neutral_zone_top_left)

        arrow_offsets = {
            "up": (0, -neutral_zone_size[1]),
            "down": (0, neutral_zone_size[1]),
            "left": (-neutral_zone_size[0], 0),
            "right": (neutral_zone_size[0], 0),
        }
        for direction, offset in arrow_offsets.items():
            arrow_image_key = (
                f"spr_{'pressed' if key_states.get(self.map_direction_to_key(direction), False) else 'unpressed'}"
                f"_arrow_{direction}"
            )
            arrow_image = self.images[arrow_image_key]
            arrow_rect = arrow_image.get_rect(
                center=(center_position[0] + offset[0], center_position[1] + offset[1])
            )
            self.screen.blit(arrow_image, arrow_rect.topleft)

    @staticmethod
    def map_direction_to_key(direction):
        direction_to_key = {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
        }
        return direction_to_key.get(direction, None)

    def blit_arrow(self, direction, is_pressed):
        image_key = "spr_pressed_arrow_" if is_pressed else "spr_unpressed_arrow_"
        image_key += direction
        rect = self.arrows[direction]
        self.screen.blit(self.images[image_key], rect.topleft)

    def handle_click(self, mouse_pos):
        self.center_position = mouse_pos

        if self.neutral_zone_rect.collidepoint(mouse_pos):
            self.pressed_direction = "neutral"
        else:
            for direction, rect in self.arrows.items():
                if rect.collidepoint(mouse_pos):
                    self.pressed_direction = direction
                    break

        self.mouse_is_pressed = True
        return self.pressed_direction

    def handle_mouse_up(self):
        self.center_position = None
        last_direction = self.pressed_direction
        self.mouse_is_pressed = False
        self.pressed_direction = None
        return last_direction

    def handle_mouse_move(self, mouse_pos):
        if not self.mouse_is_pressed or self.center_position is None:
            return None

        dx = mouse_pos[0] - self.center_position[0]
        dy = mouse_pos[1] - self.center_position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        angle = math.degrees(math.atan2(-dy, dx)) % 360

        if distance > self.activation_distance:
            if 45 <= angle < 135:
                return "up"
            if 135 <= angle < 225:
                return "left"
            if 225 <= angle < 315:
                return "down"
            return "right"
        return "neutral"
