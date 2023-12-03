import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT  # Assuming you have a config.py with constants

class Player(pygame.sprite.Sprite):
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

        self.current_direction = "left"  # Default direction
        self.original_image = self.original_images[self.current_direction]
        self.original_width, self.original_height = self.original_image.get_size()

        # Initialize size_score and other properties before calling resize_player_image
        self.size_score = 0
        self.speed_power = 0
        self.speed_x, self.speed_y = 6, 6
        self.powerup_time_left, self.speed_time_left = 500, 500
        self.star_power, self.player_animate_timer = 0, 0
        self.pos = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100]

        # Initialize self.rect before calling resize_player_image
        self.rect = self.original_image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # Now call resize_player_image
        self.resize_player_image()

        # Add the player to the allsprites group
        allsprites.add(self)

        # Set initial position
        self.rect.topleft = (self.pos[0], self.pos[1])

        self.last_pressed = 0
    def update(self):
        self.rect = self.image.get_rect()
        newpos = (self.pos[0], self.pos[1])
        self.rect.topleft = newpos
        # STAR POWERUPS
        if self.star_power == 0: #no star power
            self.powerup_time_left = 500 #restart to 5 seconds
        elif self.star_power == 1: #star powerup
            self.player_animate_timer += 1
            if self.player_animate_timer > 6:
                self.player_animate_timer = 0
            self.powerup_time_left -= 1
        elif self.star_power == 2: #mini sharks
            self.powerup_time_left -= 1
        # SPEED POWERUPS/DEFECTS
        if self.speed_power == 0:
            self.speed_x, self.speed_y = 6, 6
            self.speed_time_left = 500
        elif (self.speed_power == 1 or self.speed_power == 2): # Seahorse & jellyfish
            self.speed_time_left -= 1
        # RESET TIMERS
        if self.powerup_time_left < 0: # Powerup is over on the player
            self.star_power = 0
            self.powerup_time_left = 500
        if self.speed_time_left < 0:
            self.speed_power = 0
            self.speed_time_left = 500
    def resize_player_image(self):
        # Get the original image for the current direction
        base_image = self.original_images[self.current_direction]
    
        # Scale the base image
        new_width = base_image.get_width() + self.size_score * 2
        new_height = base_image.get_height() + self.size_score * 2
        self.image = pygame.transform.smoothscale(base_image, (new_width, new_height))
    
        # Update the rect
        self.rect = self.image.get_rect(center=self.rect.center)
    def stop_movement(self):
        if self.speed_power == 1:  # Seahorse speed powerup
            self.speed_x, self.speed_y = 9, 9
        elif self.speed_power == 2:  # Jellyfish speed defect
            self.speed_x, self.speed_y = 2, 2
        else:
            self.speed_x, self.speed_y = 6, 6  # Default speed
        # Adjust player size back to normal if needed
        self.player_width, self.player_height = (41, 19)
    
        # Set appropriate image based on direction and starpower status
        if self.last_pressed == 0:  # Last pressed was left or initial state
            if self.star_power == 1:
                if self.player_animate_timer > 2:
                    self.image = self.images["player_left_gold"]
                else:
                    self.image = self.images["player_left"]
            else:
                self.image = self.images["player_left"]
        else:  # Last pressed was right
            if self.star_power == 1:
                if self.player_animate_timer > 2:
                    self.image = self.images["player_right_gold"]
                else:
                    self.image = self.images["player_right"]
            else:
                self.image = self.images["player_right"]
        self.resize_player_image()
    def move_up(self):
        self.player_width, self.player_height = (21, 42)
        self.current_direction = "up"
        self.image = self.images["player_up"]
        if self.pos[1] > 50: # Boundary, 32 is block, added a few extra pixels to make it look nicer
            self.pos[1] -= self.speed_y
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_up_gold"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_up"]
        self.resize_player_image()
    def move_down(self):
        self.player_width, self.player_height = (21, 42)
        self.current_direction = "down"
        self.image = self.images["player_down"]
        if self.pos[1] < SCREEN_HEIGHT-75:
            self.pos[1] += self.speed_y
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_down_gold"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_down"]
        self.resize_player_image()
    def move_left(self):
        self.player_width, self.player_height = (41, 19)
        self.current_direction = "left"
        self.image = self.images["player_left"]
        if self.pos[0] > 32:
            self.pos[0] -= self.speed_x
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_left_gold"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_left"]
        self.resize_player_image()
    def move_right(self):
        self.player_width, self.player_height = (41, 19)
        self.current_direction = "right"
        self.image = self.images["player_right"]
        if self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_right_gold"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_right"]
        self.resize_player_image()
    def move_up_left(self):
        self.player_width, self.player_height = (34, 34)
        self.current_direction = "up_left"
        self.image = self.images["player_up_left"]
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_up_left"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_up_left_gold"]
                
        # Update position for diagonal movement
        if self.pos[1] > 50 and self.pos[0] > 32:
            self.pos[0] -= self.speed_x
            self.pos[1] -= self.speed_y
        self.resize_player_image()
    def move_up_right(self):
        self.player_width, self.player_height = (34, 34)
        self.current_direction = "up_right"
        self.image = self.images["player_up_right"]
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_up_right"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_up_right_gold"]
                
        # Update position for diagonal movement
        if self.pos[1] > 50 and self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
            self.pos[1] -= self.speed_y  
        self.resize_player_image()
    def move_down_left(self):
        self.player_width, self.player_height = (34, 34)
        self.current_direction = "down_left"
        self.image = self.images["player_down_left"]
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_down_left_gold"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_down_left"]
        
        # Update position for diagonal movement
        if self.pos[1] < SCREEN_HEIGHT-75 and self.pos[0] > 32:
            self.pos[0] -= self.speed_x
            self.pos[1] += self.speed_y
        self.resize_player_image()
    def move_down_right(self):
        self.player_width, self.player_height = (34, 34)
        self.current_direction = "down_right"
        self.image = self.images["player_down_right"]
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_down_right_gold"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_down_right"]
                
        # Update position for diagonal movement
        if self.pos[1] < SCREEN_HEIGHT-75 and self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
            self.pos[1] += self.speed_y
        self.resize_player_image()
    def collide_with_red_fish(self, score, score_blit):
        score_blit = 1
        score += 1
        self.size_score += 1
        return score, score_blit
    def collide_with_green_fish(self, score, score_blit):
        score_blit = 2
        score += 2
        self.size_score += 2
        return score, score_blit
    def collide_with_silver_fish(self, score, score_blit):
        score_blit = 3
        score += 3
        self.size_score += 3
        return score, score_blit
    def collide_with_shark(self, score, score_blit):
        if self.star_power == 2: # Mini-sharks
            score_blit = 1
            score += 1
            self.size_score += 1
            return score, score_blit
        else:
            return score, score_blit
    def collide_with_seahorse(self):
        self.speed_power = 1
        self.speed_x, self.speed_y = 9, 9
        self.speed_time_left = 500
    def collide_with_jellyfish(self):
        self.speed_power = 2
        self.size_score = 0
        self.speed_x, self.speed_y = 2, 2
        self.speed_time_left = 500
    def collide_with_snake(self):
        self.size_score = 0
    def collide_with_star(self):
        self.star_power = random.choice([0, 1])+1
    def get_powerup_timer_text(self, font):
        if self.star_power != 0:
            return font.render("Powerup Timer: " + str((self.powerup_time_left//100)+1), 1, (255, 255, 255))
        return font.render("", 1, (0, 0, 0))
    def get_speed_timer_text(self, font):
        if self.speed_power == 1:
            return font.render("Speed Timer: " + str((self.speed_time_left//100)+1), 1, (255, 255, 255))
        elif self.speed_power == 2:
            return font.render("Sting Timer: " + str((self.speed_time_left//100)+1), 1, (255, 255, 255))
        else:
            return font.render("", 1, (0, 0, 0))
    def remove_sprite(self):
        self.kill()