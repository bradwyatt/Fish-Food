import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT  # Assuming you have a config.py with constants

class Player(pygame.sprite.Sprite):
    PLAYER_SCORE_BIGGER_THAN_BIG_GREEN_FISH = 30
    NO_STAR_POWER = 0
    INVINCIBLE_POWERUP = 1
    SHARK_SHRINKER_POWERUP = 2
    STAR_POWERUP_TIMER_IN_TICKS = 500
    NO_SPEED_POWER = 0
    SPEED_SURGE = 1
    SPEED_REDUCER = 2
    SPEED_POWERUP_TIMER_IN_TICKS = 500
    SURGE_MOVE_SPEED = 9
    REDUCER_MOVE_SPEED = 2
    REGULAR_MOVE_SPEED = 6
    STAR_POWER_SELECTED = INVINCIBLE_POWERUP
    # STAR_POWER_SELECTED = random.choice([self.INVINCIBLE_POWERUP, self.SHARK_SHRINKER_POWERUP])
    
    def __init__(self, allsprites, images):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
    
        # Store original images for each direction
        self.original_images = {
            "left": self.images["player_left"],
            "right": self.images["player_right"],
            "up": self.images["player_up"],
            "down": self.images["player_down"],
            "up_left": self.images["player_up_left"],
            "up_right": self.images["player_up_right"],
            "down_left": self.images["player_down_left"],
            "down_right": self.images["player_down_right"],
        }
        
        # Load and store mask images
        self.face_masks = {
            "left": pygame.mask.from_surface(images["player_left_face"]),
            "right": pygame.mask.from_surface(images["player_right_face"]),
            "up": pygame.mask.from_surface(images["player_up_face"]),
            "down": pygame.mask.from_surface(images["player_down_face"]),
            "up_left": pygame.mask.from_surface(images["player_up_right_face"]),
            "up_right": pygame.mask.from_surface(images["player_up_right_face"]),
            "down_left": pygame.mask.from_surface(images["player_down_left_face"]),
            "down_right": pygame.mask.from_surface(images["player_down_right_face"])
        }
        
        # Load and store full-body mask images for each direction
        self.body_masks = {
            "left": pygame.mask.from_surface(images["player_left"]),
            "right": pygame.mask.from_surface(images["player_right"]),
            "up": pygame.mask.from_surface(images["player_up"]),
            "down": pygame.mask.from_surface(images["player_down"]),
            "up_left": pygame.mask.from_surface(images["player_up_left"]),
            "up_right": pygame.mask.from_surface(images["player_up_right"]),
            "down_left": pygame.mask.from_surface(images["player_down_left"]),
            "down_right": pygame.mask.from_surface(images["player_down_right"])
        }
    
        self.current_direction = "left"  # Default direction
        self.original_image = self.original_images[self.current_direction]
        self.original_width, self.original_height = self.original_image.get_size()
    
        # Initialize size_score and other properties
        self.size_score = 0
        self.speed_power = self.NO_SPEED_POWER
        self.speed_x, self.speed_y = self.REGULAR_MOVE_SPEED, self.REGULAR_MOVE_SPEED
        self.powerup_time_left, self.speed_time_left = 0, 0
        self.star_power = self.NO_STAR_POWER
        self.player_animate_timer = 0
        self.pos = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100]
    
        # Initialize self.rect and self.image
        self.image = self.original_image  # Set initial image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    
        # Resize the player image based on the initial image
        self.resize_player_image_and_masks(self.image)
    
        # Add the player to the allsprites group
        allsprites.add(self)
    
        # Set initial position
        self.rect.topleft = (self.pos[0], self.pos[1])
    
        self.last_pressed = 0
        self.face_mask = self.face_masks[self.current_direction]  # Initialize face mask
        self.body_mask = self.body_masks[self.current_direction]  # Initialize body mask


        

    def update(self):
        # Update the position of the player
        self.rect = self.image.get_rect()
        newpos = (self.pos[0], self.pos[1])
        self.rect.topleft = newpos
    
        # Update the player's size and masks first, using the current image
        self.resize_player_image_and_masks(self.image)
    
        # Handle star power animation for invincibility
        if self.star_power == self.INVINCIBLE_POWERUP:
            self.player_animate_timer += 1
    
            # Toggle between gold and normal image based on the animate timer
            if self.player_animate_timer % 10 < 5:
                gold_image_key = "player_" + self.current_direction + "_gold"
                if gold_image_key in self.images:
                    self.image = self.images[gold_image_key]
                else:
                    self.image = self.original_images[self.current_direction]
            else:
                self.image = self.original_images[self.current_direction]
    
            self.resize_player_image_and_masks(self.image)
    
            # Reset the animation timer if it reaches a certain threshold
            if self.player_animate_timer >= 20:  # Adjust the value for animation speed
                self.player_animate_timer = 0
        else:
            # Use the normal image and update image and mask
            self.image = self.original_images[self.current_direction]
            self.resize_player_image_and_masks(self.image)
    
        # Decrement powerup timer and reset if over for both star_power 1 and 2
        if self.star_power > self.NO_STAR_POWER:
            self.powerup_time_left -= 1
            if self.powerup_time_left < 0:  # Powerup is over
                self.star_power = self.NO_STAR_POWER
    
        # Handle speed powerups/defects
        if self.speed_power > self.NO_SPEED_POWER:
            self.speed_time_left -= 1
            if self.speed_time_left < 0:  # Speed change is over
                self.speed_power = self.NO_SPEED_POWER
                self.speed_x, self.speed_y = self.REGULAR_MOVE_SPEED, self.REGULAR_MOVE_SPEED  # Reset to default speed


    def resize_player_image_and_masks(self, base_image):
        # Scale the base image (player's main image)
        new_width = base_image.get_width() + self.size_score * 2
        new_height = base_image.get_height() + self.size_score * 2
        self.image = pygame.transform.smoothscale(base_image, (new_width, new_height))

        # Get the corresponding face mask image based on the current direction
        face_mask_key = "player_" + self.current_direction + "_face"
        face_mask_image = self.images[face_mask_key]

        # Scale the corresponding face mask image
        face_mask_image = pygame.transform.smoothscale(face_mask_image, (new_width, new_height))
        
        # Update the mask from the resized face mask image
        self.face_mask = pygame.mask.from_surface(face_mask_image)
        
        # Scale the corresponding full-body mask image
        body_mask_image = self.images["player_" + self.current_direction]
        body_mask_image = pygame.transform.smoothscale(body_mask_image, (new_width, new_height))
        self.body_mask = pygame.mask.from_surface(body_mask_image)

        # Update the rect
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_player_image(self):
        # Handle star power animation for invincibility
        if self.star_power == self.INVINCIBLE_POWERUP:
            self.player_animate_timer += 1
    
            # Toggle between gold and normal image based on the animate timer
            if self.player_animate_timer % 10 < 5:
                gold_image_key = "player_" + self.current_direction + "_gold"
                if gold_image_key in self.images:
                    self.image = self.images[gold_image_key]
                else:
                    self.image = self.original_images[self.current_direction]
            else:
                self.image = self.original_images[self.current_direction]
    
            # Reset the animation timer if it reaches a certain threshold
            if self.player_animate_timer >= 20:  # Adjust for animation speed
                self.player_animate_timer = 0
        else:
            # Use the normal image for non-invincible state
            self.image = self.original_images[self.current_direction]
    
        # Resize the player image and update masks
        self.resize_player_image_and_masks(self.image)

    def stop_movement(self):
        if self.speed_power == self.INVINCIBLE_POWERUP:  # Seahorse speed powerup
            self.speed_x, self.speed_y = self.SURGE_MOVE_SPEED, self.SURGE_MOVE_SPEED
        elif self.speed_power == self.SHARK_SHRINKER_POWERUP:  # Jellyfish speed defect
            self.speed_x, self.speed_y = self.REDUCER_MOVE_SPEED, self.REDUCER_MOVE_SPEED
        else:
            self.speed_x, self.speed_y = self.REGULAR_MOVE_SPEED, self.REGULAR_MOVE_SPEED  # Default speed
    def move_up(self):
        self.current_direction = "up"
        if self.pos[1] > 50:  # Boundary check
            self.pos[1] -= self.speed_y
    
        # Update the player image based on the current state
        self.update_player_image()
    def move_down(self):
        self.current_direction = "down"
        if self.pos[1] < SCREEN_HEIGHT-75:
            self.pos[1] += self.speed_y
        self.update_player_image()
    def move_left(self):
        self.current_direction = "left"
        if self.pos[0] > 32:
            self.pos[0] -= self.speed_x
        self.update_player_image()
    def move_right(self):
        self.current_direction = "right"
        if self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
        self.update_player_image()
    def move_up_left(self):
        self.current_direction = "up_left"
                
        # Update position for diagonal movement
        if self.pos[1] > 50 and self.pos[0] > 32:
            self.pos[0] -= self.speed_x
            self.pos[1] -= self.speed_y
        self.update_player_image()
    def move_up_right(self):
        self.current_direction = "up_right"
                
        # Update position for diagonal movement
        if self.pos[1] > 50 and self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
            self.pos[1] -= self.speed_y
        self.update_player_image()
    def move_down_left(self):
        self.current_direction = "down_left"
        
        # Update position for diagonal movement
        if self.pos[1] < SCREEN_HEIGHT-75 and self.pos[0] > 32:
            self.pos[0] -= self.speed_x
            self.pos[1] += self.speed_y
        self.update_player_image()
    def move_down_right(self):
        self.current_direction = "down_right"
                
        # Update position for diagonal movement
        if self.pos[1] < SCREEN_HEIGHT-75 and self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
            self.pos[1] += self.speed_y
        self.update_player_image()
    def collide_with_seahorse(self):
        self.speed_power = self.SPEED_SURGE
        self.speed_x, self.speed_y = self.SURGE_MOVE_SPEED, self.SURGE_MOVE_SPEED
        self.speed_time_left += self.SPEED_POWERUP_TIMER_IN_TICKS
    def collide_with_jellyfish(self):
        self.speed_power = self.SPEED_REDUCER
        self.size_score = 0
        self.speed_x, self.speed_y = self.REDUCER_MOVE_SPEED, self.REDUCER_MOVE_SPEED
        self.speed_time_left += self.SPEED_POWERUP_TIMER_IN_TICKS
    def collide_with_snake(self):
        self.size_score = 0
    def collide_with_star(self):
        self.star_power = self.STAR_POWER_SELECTED
        self.powerup_time_left += self.STAR_POWERUP_TIMER_IN_TICKS
    def get_powerup_timer_text(self, font):
        if self.star_power != self.NO_STAR_POWER:
            return font.render("Powerup Timer: " + str((self.powerup_time_left//100)+1), 1, (255, 255, 255))
        return font.render("", 1, (0, 0, 0))
    def get_speed_timer_text(self, font):
        if self.speed_power == self.SPEED_SURGE:
            return font.render("Speed Timer: " + str((self.speed_time_left//100)+1), 1, (255, 255, 255))
        elif self.speed_power == self.SPEED_REDUCER:
            return font.render("Sting Timer: " + str((self.speed_time_left//100)+1), 1, (255, 255, 255))
        else:
            return font.render("", 1, (0, 0, 0))
    def remove_sprite(self):
        self.kill()