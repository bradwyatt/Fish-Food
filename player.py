import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT  # Assuming you have a config.py with constants

class Player(pygame.sprite.Sprite):
    def __init__(self, allsprites, images):
        """
        Main fish that player controls in the game
        Ability to grow to eat smaller fish (prey)
        """
        pygame.sprite.Sprite.__init__(self, allsprites)
        self.images = images
        self.image = self.images["player_left"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.player_width, self.player_height = (41, 19)
        self.size_score = 0
        self.speed_power = 0
        self.speed_x, self.speed_y = 6, 6
        self.powerup_time_left, self.speed_time_left = 500, 500
        self.star_power, self.player_animate_timer = 0, 0
        self.pos = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2+100]
        self.rect.topleft = (self.pos[0], self.pos[1])
        self.last_pressed = 0
    def update(self):
        self.rect = self.image.get_rect()
        newpos = (self.pos[0], self.pos[1])
        self.rect.topleft = newpos
        # GROW
        if self.size_score < 0:
            self.size_score = 0
        if self.size_score > 40:
            self.size_score = 40
        self.image = pygame.transform.smoothscale(self.image, (self.player_width+self.size_score, self.player_height+self.size_score))
        self.rect.inflate_ip(self.size_score, self.size_score)
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
                    self.image = pygame.transform.rotate(self.images["player_left_gold"], 180)
                    self.image = pygame.transform.flip(self.image, 0, 1)
                else:
                    self.image = pygame.transform.rotate(self.images["player_left"], 180)
                    self.image = pygame.transform.flip(self.image, 0, 1)
            else:
                self.image = pygame.transform.rotate(self.images["player_left"], 180)
                self.image = pygame.transform.flip(self.image, 0, 1)

    def move_up(self):
        self.player_width, self.player_height = (21, 42)
        self.image = pygame.transform.flip(self.images["player_down"], 1, 1)
        if self.pos[1] > 50: # Boundary, 32 is block, added a few extra pixels to make it look nicer
            self.pos[1] -= self.speed_y
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = pygame.transform.flip(self.images["player_down_gold"], 1, 1)
            if self.player_animate_timer > 4:
                self.image = pygame.transform.flip(self.images["player_down"], 1, 1)
    def move_down(self):
        self.player_width, self.player_height = (21, 42)
        self.image = self.images["player_down"]
        if self.pos[1] < SCREEN_HEIGHT-75:
            self.pos[1] += self.speed_y
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_down_gold"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_down"]
    def move_left(self):
        self.player_width, self.player_height = (41, 19)
        self.image = self.images["player_left"]
        if self.pos[0] > 32:
            self.pos[0] -= self.speed_x
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = self.images["player_left_gold"]
            if self.player_animate_timer > 4:
                self.image = self.images["player_left"]
    def move_right(self):
        self.player_width, self.player_height = (41, 19)
        self.image = pygame.transform.rotate(self.images["player_left"], 180)
        self.image = pygame.transform.flip(self.image, 0, 1)
        if self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = pygame.transform.rotate(self.images["player_left_gold"], 180)
                self.image = pygame.transform.flip(self.image, 0, 1)
            if self.player_animate_timer > 4:
                self.image = pygame.transform.rotate(self.images["player_left"], 180)
                self.image = pygame.transform.flip(self.image, 0, 1)
    def move_up_left(self):
        self.player_width, self.player_height = (34, 34)
        self.image = pygame.transform.flip(self.images["player_down_right"], 0, 1)
        self.image = pygame.transform.rotate(self.image, 90)
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = pygame.transform.flip(self.images["player_down_right"], 0, 1)
                self.image = pygame.transform.rotate(self.image, 90)
            if self.player_animate_timer > 4:
                self.image = pygame.transform.flip(self.images["player_down_right_gold"], 0, 1)
                self.image = pygame.transform.rotate(self.image, 90)
                
        # Update position for diagonal movement
        if self.pos[1] > 50 and self.pos[0] > 32:
            self.pos[0] -= self.speed_x
            self.pos[1] -= self.speed_y
            
    def move_up_right(self):
        self.player_width, self.player_height = (34, 34)
        self.image = pygame.transform.rotate(self.images["player_down_right"], 90)
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = pygame.transform.rotate(self.images["player_down_right"], 90)
            if self.player_animate_timer > 4:
                self.image = pygame.transform.rotate(self.images["player_down_right_gold"], 90)
                
        # Update position for diagonal movement
        if self.pos[1] > 50 and self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
            self.pos[1] -= self.speed_y  
            
    def move_down_left(self):
        self.player_width, self.player_height = (34, 34)
        self.image = pygame.transform.flip(self.images["player_down_right"], 1, 0)
        if self.star_power == 1:
            if self.player_animate_timer > 2:
                self.image = pygame.transform.flip(self.images["player_down_right_gold"], 1, 0)
            if self.player_animate_timer > 4:
                self.image = pygame.transform.flip(self.images["player_down_right"], 1, 0)
        
        # Update position for diagonal movement
        if self.pos[1] < SCREEN_HEIGHT-75 and self.pos[0] > 32:
            self.pos[0] -= self.speed_x
            self.pos[1] += self.speed_y
            
    def move_down_right(self):
        self.player_width, self.player_height = (34, 34)
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