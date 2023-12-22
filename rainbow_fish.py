import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT  # Assuming you have a config.py with constants

class RainbowFish(pygame.sprite.Sprite):
    MAX_SIZE = [85, 65]  # Maximum size for the RainbowFish

    def __init__(self, allsprites, images):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.image = self.images["spr_rainbow_fish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.score_exit = 0
        self.rainbow_timer = 0
        self.size = [55, 35]
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -400)
        self.rect.topleft = self.pos
        self.arrow_warning = 0
        self.activate = 0
        self.chase = 0

    def update(self):
        self.rect.topleft = (self.pos[0], self.pos[1])
        self.rainbow_timer += 1

        # Handling fish movement and size
        if self.activate == 1:
            self.handle_activation()

    def handle_behavior(self, player_size_score, player_star_power, player_pos):
        """
        Determine whether to chase or avoid the player based on the player's state
        and position.
        """
        # Only activate chasing or avoiding behavior if the fish is active and not exiting
        if self.activate and not self.score_exit:
            if self.size[0] - 45 <= player_size_score or player_star_power == 1:
                self.avoid_player(player_pos)
            else:
                self.chase_player(player_pos)

    def handle_activation(self):
        if self.rainbow_timer >= 2000 or self.score_exit == 1:
            self.return_to_top()

        elif self.rainbow_timer >= 300 and self.pos[1] < 200 and self.chase == 0 and self.score_exit == 0: 
            self.move_down()

    def return_to_top(self):
        self.chase = 0
        if self.pos[1] > -100:
            self.score_exit = 1
            self.pos = (self.pos[0], self.pos[1] - 3)
        else:
            self.reset_fish()
    
    def move_down(self):
        self.arrow_warning = 1
        self.image = pygame.transform.smoothscale(self.image, (self.size[0], self.size[1]))
        self.pos = (self.pos[0], self.pos[1] + 2)
        if self.pos[1] >= 100:
            self.arrow_warning = 0

    def reset_fish(self):
        self.activate = 0
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
        self.rainbow_timer, self.score_exit = 0, 0
        if self.size[0] < self.MAX_SIZE[0] and self.size[1] < self.MAX_SIZE[1]:
            self.size[0] += 10
            self.size[1] += 10
            self.size[0] = min(self.size[0], self.MAX_SIZE[0])
            self.size[1] = min(self.size[1], self.MAX_SIZE[1])
        self.image = self.images["spr_rainbow_fish"]
    
    def avoid_player(self, player_pos):
        #Avoid Player
        if self.pos[0] > player_pos[0]:
            self.pos = (self.pos[0]+2, self.pos[1])
        elif self.pos[0] < player_pos[0]:
            self.pos = (self.pos[0]-2, self.pos[1])
        if self.pos[1] < player_pos[1]:
            self.pos = (self.pos[0], self.pos[1]-2)
        elif self.pos[1] > player_pos[1]:
            self.pos = (self.pos[0], self.pos[1]+2)
        # Rainbow fish can't go past walls, must go up if stuck
        if(self.pos[0] < 0 or self.pos[0] > SCREEN_WIDTH-32):
            self.score_exit = 1
            self.chase = 0
        elif(self.pos[1] < 32 or self.pos[1] > SCREEN_HEIGHT-32):
            self.score_exit = 1
            self.chase = 0
                
    def chase_player(self, player_pos):
        if self.pos[0] > player_pos[0]:
            self.pos = (self.pos[0]-1, self.pos[1])
        elif self.pos[0] < player_pos[0]:
            self.pos = (self.pos[0]+1, self.pos[1])
        if self.pos[1] < player_pos[1]:
            self.pos = (self.pos[0], self.pos[1]+1)
        elif self.pos[1] > player_pos[1]:
            self.pos = (self.pos[0], self.pos[1]-1)

    def collide_with_player(self):
        self.rainbow_timer = 0
        self.activate = 0
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
        if self.size[0]-20 <= 55: #increases till max size
            self.size[0] += 10
            self.size[1] += 10
    def collide_with_bright_blue_fish(self):
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
        self.rainbow_timer = 0
    def remove_sprite(self):
        self.kill()