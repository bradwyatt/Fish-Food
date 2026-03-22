import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT  # Assuming you have a config.py with constants

class Shark(pygame.sprite.Sprite):
    TURN_TIME_MS = 50
    # SHARKS_SCORES_TO_SPAWN = [5]
    SHARKS_SCORES_TO_SPAWN = [5, 20, 45, 75]
    MOVE_SPEED = 3
    PLAYER_SCORE_VALUE = 2
    Y_POSITION_SPAWN = -300
    Y_POSITION_TO_START_PLAYING = 125
    OFFSET_FROM_WALL = 10
    DESCEND_SPEED = 1
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
        self.face_image = images["spr_shark_face_left"]  # Shark's face image for collision detection
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]),
                          random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]))
        self.mini_shark = False
        self.activate = False
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), self.Y_POSITION_SPAWN)
        self.stop_timer = 0  # Timer for stopping the shark
        self.initial_descent_complete = False
        self.mask = pygame.mask.from_surface(self.face_image)  # Create a mask from the shark image
        self._appearance_cache = {}
        self._appearance_dirty = True
        self._last_direction_sign = -1 if self.direction[0] < 0 else 1
        self._last_mini_shark = self.mini_shark

        self.game_over = False
    def update(self):
        if self.game_over:
            return
        current_direction_sign = -1 if self.direction[0] < 0 else 1
        if current_direction_sign != self._last_direction_sign:
            self._last_direction_sign = current_direction_sign
            self._appearance_dirty = True
        if self.mini_shark != self._last_mini_shark:
            self._last_mini_shark = self.mini_shark
            self._appearance_dirty = True
        if self.activate and not self.initial_descent_complete:
            if self.rect.top < self.Y_POSITION_TO_START_PLAYING:
                self.rect.y += self.DESCEND_SPEED # Move the shark downwards until it is fully visible
            else:
                self.initial_descent_complete = True
            self.update_image_and_mask()
        else:
            current_time = pygame.time.get_ticks()
    
            # Check if the turning period has elapsed
            if self.stop_timer > current_time:
                # During the turning time, keep the turning sprite
                self.image = self._get_turning_image()
                # Do not move while in turning animation
            else:
                # After the turning period, update the sprite based on direction
                self.update_image_and_mask()
    
                # Regular movement code, allows movement after the turning period
                self.move_shark()
    def update_image_and_mask(self):
        cache_key = ("mini" if self.mini_shark else "full", "right" if self.direction[0] > 0 else "left")
        cached_appearance = self._appearance_cache.get(cache_key)
        if cached_appearance is None:
            if self.mini_shark:
                image_key = "spr_shark_right" if self.direction[0] > 0 else "spr_shark_left"
                scaled_image = pygame.transform.smoothscale(self.images[image_key], (60, 30))
                cached_appearance = {
                    "image": scaled_image,
                    "mask": pygame.mask.from_surface(scaled_image),
                    "face_image": None,
                }
            else:
                image_key = "spr_shark_right" if self.direction[0] > 0 else "spr_shark_left"
                face_key = "spr_shark_face_right" if self.direction[0] > 0 else "spr_shark_face_left"
                face_image = self.images[face_key]
                cached_appearance = {
                    "image": self.images[image_key],
                    "mask": pygame.mask.from_surface(face_image),
                    "face_image": face_image,
                }
            self._appearance_cache[cache_key] = cached_appearance

        self.image = cached_appearance["image"]
        self.face_image = cached_appearance["face_image"]
        self.mask = cached_appearance["mask"]
        self._appearance_dirty = False

    def _get_turning_image(self):
        cache_key = ("turning", self.mini_shark)
        turning_image = self._appearance_cache.get(cache_key)
        if turning_image is None:
            if self.mini_shark:
                turning_image = pygame.transform.smoothscale(self.images["spr_shark_turning"], (60, 30))
            else:
                turning_image = self.images["spr_shark_turning"]
            self._appearance_cache[cache_key] = turning_image
        return turning_image
    def move_shark(self):
        if self.rect.topleft[1] >= 0:
            newpos = self.rect.topleft[0] + self.direction[0], self.rect.topleft[1] + self.direction[1]
            self.rect.topleft = newpos
    def collision_with_wall(self, rect):
        if self.rect.colliderect(rect):
            # Change direction immediately on collision
            self.update_direction()

            # Trigger the turning animation for a set duration
            self.stop_timer = pygame.time.get_ticks() + Shark.TURN_TIME_MS

            # Offset the shark from the wall
            self.offset_from_wall()


    def offset_from_wall(self):
        # Offset the shark away from the wall based on its new direction
        if self.direction[0] > 0:  # Moving right
            self.rect.left += self.OFFSET_FROM_WALL
        elif self.direction[0] < 0:  # Moving left
            self.rect.right -= self.OFFSET_FROM_WALL
        if self.direction[1] > 0:  # Moving down
            self.rect.top += self.OFFSET_FROM_WALL
        elif self.direction[1] < 0:  # Moving up
            self.rect.bottom -= self.OFFSET_FROM_WALL
    def update_direction(self):
        # Determine the new direction based on which wall the shark collided with
        # The actual direction update happens after the turning animation
        if self.rect.left < 32:  # Collided with left wall
            self.direction = (self.MOVE_SPEED, random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]))
        elif self.rect.right > SCREEN_WIDTH - 32:  # Collided with right wall
            self.direction = (-self.MOVE_SPEED, random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]))
        elif self.rect.top < 32:  # Collided with top wall
            self.direction = (random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]), self.MOVE_SPEED)
        elif self.rect.bottom > SCREEN_HEIGHT - 64:  # Collided with bottom wall
            self.direction = (random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]), -self.MOVE_SPEED)

        self._appearance_dirty = True
    def handle_timer_event(self):
        # This method should be called when a USEREVENT + 1 is triggered
        if self.rect.left < 32:  # Left walls
            self.direction = (3, random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]))
        elif self.rect.top > SCREEN_HEIGHT - 64:  # Bottom walls
            self.direction = (random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]), -self.MOVE_SPEED)
        elif self.rect.right > SCREEN_WIDTH - 32:  # Right walls
            self.direction = (-self.MOVE_SPEED, random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]))
        elif self.rect.top < 32:  # Top walls
            self.direction = (random.choice([-self.MOVE_SPEED, self.MOVE_SPEED]), self.MOVE_SPEED)

        # Update sprite based on new direction
        if self.direction[0] > 0:
            self.image = self.images["spr_shark_right"]
        else:
            self.image = self.images["spr_shark_left"]
    def reinitialize_for_next_spawn(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), self.Y_POSITION_SPAWN)
        self.initial_descent_complete = False
    def collide_with_bright_blue_fish(self):
        self.reinitialize_for_next_spawn()
    def collide_with_player(self):
        self.reinitialize_for_next_spawn()
    def get_score_value(self):
        return self.PLAYER_SCORE_VALUE
    def remove_sprite(self):
        self.kill()
