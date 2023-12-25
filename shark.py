import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT  # Assuming you have a config.py with constants

class Shark(pygame.sprite.Sprite):
    TURN_TIME_MS = 1000
    def __init__(self, allsprites, images):
        """
        Most frequently-seen predator in the game.
        Starts coming from above and then bounces around the room
        Only time player can avoid:
        When player has a star powerup, shark respawns
        When player has mini shark powerup, they can eat sharks
        """
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.image = images["spr_shark_left"]
        self.face_image = images["spr_shark_face"]  # Shark's face image for collision detection
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice([-3, 3]), random.choice([-3, 3]))
        self.mini_shark = 0
        self.activate = 0
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), 100)
        self.arrow_warning = 0
        self.stop_timer = 0  # Timer for stopping the shark
        self.mask = pygame.mask.from_surface(self.face_image)  # Create a mask from the shark image
    def update(self):
        current_time = pygame.time.get_ticks()

        # Check if the shark is in stop mode and if the stop period has elapsed
        if self.stop_timer > current_time:
            return
        elif self.stop_timer:
            self.update_direction()
            # Move slightly in the new direction to ensure it's not stuck on the wall
            self.rect.move_ip(self.direction[0] * 10, self.direction[1] * 10)
            self.stop_timer = 0

        # Regular movement code
        self.move_shark()

        # Update image and mask
        self.update_image_and_mask()
    def update_image_and_mask(self):
        # Update image based on mini shark state and direction
        if self.mini_shark == 1:
            self.image = pygame.transform.smoothscale(self.images["spr_mini_shark"], (60, 30))
            self.face_image = pygame.transform.smoothscale(self.face_image, (60, 30))
        else:
            if self.direction[0] > 0:
                self.image = self.images["spr_shark_right"]
            else:
                self.image = self.images["spr_shark_left"]
        self.mask = pygame.mask.from_surface(self.face_image)
    def move_shark(self):
        if not self.arrow_warning and self.rect.topleft[1] >= 0:
            newpos = self.rect.topleft[0] + self.direction[0], self.rect.topleft[1] + self.direction[1]
            self.rect.topleft = newpos
    def collision_with_wall(self, rect):
        if self.rect.colliderect(rect):
            self.stop_timer = pygame.time.get_ticks() + Shark.TURN_TIME_MS
            self.image = self.images["spr_shark_turning"]
            self.update_direction()  # Update the direction based on wall collision
            self.offset_from_wall()  # Offset the shark after updating the direction

    def offset_from_wall(self):
        # Offset the shark away from the wall based on its new direction
        if self.direction[0] > 0:  # Moving right
            self.rect.left += 10
        elif self.direction[0] < 0:  # Moving left
            self.rect.right -= 10
        if self.direction[1] > 0:  # Moving down
            self.rect.top += 10
        elif self.direction[1] < 0:  # Moving up
            self.rect.bottom -= 10
    def update_direction(self):
        # Determine which wall the shark is colliding with and update the direction
        if self.rect.left < 32:  # Collided with left wall
            self.direction = (3, random.choice([-3, 3]))
        elif self.rect.right > SCREEN_WIDTH - 32:  # Collided with right wall
            self.direction = (-3, random.choice([-3, 3]))
        elif self.rect.top < 32:  # Collided with top wall
            self.direction = (random.choice([-3, 3]), 3)
        elif self.rect.bottom > SCREEN_HEIGHT - 64:  # Collided with bottom wall
            self.direction = (random.choice([-3, 3]), -3)

        # Update sprite based on new direction
        if self.direction[0] > 0:
            self.image = self.images["spr_shark_right"]
        else:
            self.image = self.images["spr_shark_left"]
    def handle_timer_event(self):
        # This method should be called when a USEREVENT + 1 is triggered
        if self.rect.left < 32:  # Left walls
            self.direction = (3, random.choice([-3, 3]))
        elif self.rect.top > SCREEN_HEIGHT - 64:  # Bottom walls
            self.direction = (random.choice([-3, 3]), -3)
        elif self.rect.right > SCREEN_WIDTH - 32:  # Right walls
            self.direction = (-3, random.choice([-3, 3]))
        elif self.rect.top < 32:  # Top walls
            self.direction = (random.choice([-3, 3]), 3)

        # Update sprite based on new direction
        if self.direction[0] > 0:
            self.image = self.images["spr_shark_right"]
        else:
            self.image = self.images["spr_shark_left"]
    def collide_with_bright_blue_fish(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), -100)
    def collide_with_player(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), -100)
    def remove_sprite(self):
        self.kill()
