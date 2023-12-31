import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT

class BrightBlueFish(pygame.sprite.Sprite):
    OFFSCREEN_LEFT = -1000
    OFFSCREEN_RIGHT = SCREEN_WIDTH + 1000
    MOVEMENT_SPEED = 4
    ARROW_REMOVAL_BOUNDARY = -200
    LEFT_SCREEN_BOUNDARY = -300
    SPAWN_Y_RANGE = (50, SCREEN_HEIGHT - 200)
    ACTIVATION_SCORE = 50
    DIR_LEFT = 0
    DIR_RIGHT = 1

    def __init__(self, allsprites, images):
        super().__init__()
        self.images = images
        self.direction = random.choice([self.DIR_LEFT, self.DIR_RIGHT])  # 0: move left, 1: move right
        self.activate = False
        self.arrow_warning = False
        self.initialize_sprite(allsprites)
        self.reset_position()
        
    def is_out_of_world(self):
        # Check if the fish is outside the game world boundaries
        return self.rect.right < 0 or self.rect.left > SCREEN_WIDTH
    
    def try_activate(self, score, last_activation_score):
        # Check if the score has crossed the next multiple of ACTIVATION_SCORE since the last activation
        if (last_activation_score // self.ACTIVATION_SCORE < score // self.ACTIVATION_SCORE 
            and score >= self.ACTIVATION_SCORE 
            and self.is_out_of_world()):
            self.activate_fish()
            return True  # Return True to indicate that the fish has been activated
        return False
    
    def activate_fish(self):
        self.direction = random.choice([self.DIR_LEFT, self.DIR_RIGHT])
        self.activate = True
        if self.direction == self.DIR_RIGHT:  # Moving right
            self.rect.topright = (-500, random.randrange(50, SCREEN_HEIGHT - 200))
        else:  # Moving left
            self.rect.topleft = (SCREEN_WIDTH + 500, random.randrange(50, SCREEN_HEIGHT - 200))

    def initialize_sprite(self, allsprites):
        self.image = self.images["spr_bright_blue_fish_right"]
        self.rect = self.image.get_rect()
        allsprites.add(self)

    def reset_position(self):
        x_position = random.choice([self.OFFSCREEN_LEFT, self.OFFSCREEN_RIGHT])
        y_position = random.randrange(*self.SPAWN_Y_RANGE)
        self.rect.topleft = (x_position, y_position)

    def update(self):
        if self.activate:
            self.update_movement_and_images()
            self.update_mask()
        else:
            self.image = self.images["spr_bright_blue_fish_right"]
            self.mask = pygame.mask.from_surface(self.images["spr_bright_blue_fish_right_face"])  # Default mask

    def update_mask(self):
        # Update the mask based on the current direction of the fish
        if self.direction == self.DIR_RIGHT:  # Moving right
            self.mask = pygame.mask.from_surface(self.images["spr_bright_blue_fish_right_face"])
        elif self.direction == self.DIR_LEFT:  # Moving left
            self.mask = pygame.mask.from_surface(self.images["spr_bright_blue_fish_left_face"])

    def update_movement_and_images(self):
        self.arrow_warning = True
        if self.direction == self.DIR_RIGHT:  # Moving right
            self.image = self.images["spr_bright_blue_fish_right"]
            self.rect.move_ip(self.MOVEMENT_SPEED, 0)
            self.manage_boundaries_for_right_movement()
        elif self.direction == self.DIR_LEFT:  # Moving left
            self.image = self.images["spr_bright_blue_fish_left"]
            self.rect.move_ip(-self.MOVEMENT_SPEED, 0)
            self.manage_boundaries_for_left_movement()

    def manage_boundaries_for_right_movement(self):
        if self.rect.right > self.ARROW_REMOVAL_BOUNDARY:
            self.arrow_warning = False
        if self.rect.left > SCREEN_WIDTH:
            self.activate = False

    def manage_boundaries_for_left_movement(self):
        if self.rect.left <= SCREEN_WIDTH:
            self.arrow_warning = False
        if self.rect.right < self.LEFT_SCREEN_BOUNDARY:
            self.activate = False

    def remove_sprite(self):
        self.kill()
