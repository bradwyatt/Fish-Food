import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT  # Assuming you have a config.py with constants
from base_enemy import BaseEnemy

class RedFish(BaseEnemy):
    EDGE_PADDING = 100
    CHANGE_DIR_RANGE = (100, 600)
    MOVE_SPEED = 2
    SPEED_CHOICES = [-MOVE_SPEED, MOVE_SPEED]
    WALL_PADDING = 32
    BOTTOM_WALL_Y = SCREEN_HEIGHT - 64
    RIGHT_WALL_X = SCREEN_WIDTH - 32
    PLAYER_SCORE_VALUE = 1

    def __init__(self, allsprites, images):
        super().__init__()
        self.images = images
        self.original_image = images["spr_red_fish"]  # Save the original image
        self.rect = self.original_image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice(self.SPEED_CHOICES), random.choice(self.SPEED_CHOICES))
        self.change_dir_timer = 0

        # Initialize the alpha surface here, before calling reset_position
        self.alpha = 0
        self.rebuild_alpha_surface()

        self.reset_position()

    def update(self):
        self.rect.move_ip(*self.direction)
        self.change_dir_timer += 1
        self.update_image_direction()
        self.change_direction_randomly()
        self.update_fade_in()

        # Use alpha surface as the sprite's image for rendering
        self.image = self.alpha_surface

        
    def init_fade_in(self):
        self.begin_fade_in()

    def update_image_direction(self):
        # Update the original_image based on the current direction
        if self.direction[0] == -2:
            self.original_image = pygame.transform.flip(self.images["spr_red_fish"], True, False)
        elif self.direction[0] == 2:
            self.original_image = self.images["spr_red_fish"]

        # Update the alpha surface with the new image direction
        self.rebuild_alpha_surface()


    def change_direction_randomly(self):
        if self.change_dir_timer > random.randrange(*self.CHANGE_DIR_RANGE):
            self.direction = random.choice([(self.direction[0] * -1, self.direction[1]),
                                            (self.direction[0], self.direction[1] * -1),
                                            (self.direction[0] * -1, self.direction[1] * -1)])
            self.change_dir_timer = 0

    def collision_with_wall(self, rect):
        if self.rect.colliderect(rect):
            self.change_dir_timer = 0
            self.bounce_off_walls()

    def bounce_off_walls(self):
        if self.rect.left < self.WALL_PADDING:  # Left wall
            self.direction = (self.MOVE_SPEED, random.choice(self.SPEED_CHOICES))
        elif self.rect.top > self.BOTTOM_WALL_Y:  # Bottom wall
            self.direction = (random.choice(self.SPEED_CHOICES), -self.MOVE_SPEED)
        elif self.rect.right > self.RIGHT_WALL_X:  # Right wall
            self.direction = (-self.MOVE_SPEED, random.choice(self.SPEED_CHOICES))
        elif self.rect.top < self.WALL_PADDING:  # Top wall
            self.direction = (random.choice(self.SPEED_CHOICES), self.MOVE_SPEED)

    def _prepare_for_reset(self):
        self.alpha = 0
        self.alpha_surface.set_alpha(self.alpha)
        self.change_dir_timer = 0

    def _random_spawn_position(self):
        return (
            random.randrange(self.EDGE_PADDING, SCREEN_WIDTH - self.EDGE_PADDING),
            random.randrange(self.EDGE_PADDING, SCREEN_HEIGHT - self.EDGE_PADDING),
        )

    def _finish_reset(self):
        self.begin_fade_in()

    def collide_with_player(self):
        self.reset_position()
        
    def get_score_value(self):
        return self.PLAYER_SCORE_VALUE

    def collide_with_bright_blue_fish(self):
        self.reset_position()

    def collide_with_green_fish(self):
        self.reset_position()

    def remove_sprite(self):
        self.kill()
