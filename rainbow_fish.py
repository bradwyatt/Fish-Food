import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT  # Assuming you have a config.py with constants

class RainbowFish(pygame.sprite.Sprite):
    MAX_SIZE = [85, 65]  # Maximum size for the RainbowFish
    TURN_TIME_MS = 50
    def __init__(self, allsprites, images):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.image = self.images["spr_rainbow_fish_left"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.is_exiting = 0
        self.rainbow_timer = 0
        self.size = [55, 35]
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -400)
        self.rect.topleft = self.pos
        self.arrow_warning_shown = 0
        self.is_active = 0
        self.initial_descent_complete = False  # New attribute to track initial descent
        
        self.current_direction = "left"  # Default direction
        self.is_turning = False
        self.turning_timer = 0
        self.player_position = (0, 0)  # Initialize player position
        
    def update_player_position(self, player_pos):
        """Update the player's position for the Rainbow Fish."""
        self.player_position = player_pos

    def update(self):
        self.rainbow_timer += 1
        # Update size and mask
        self.image = pygame.transform.smoothscale(self.image, (self.size[0], self.size[1]))
        self.mask = pygame.mask.from_surface(self.image)

        # Check player position relative to Rainbow Fish
        player_on_left = self.player_position[0] < self.rect.centerx
        player_on_right = self.player_position[0] > self.rect.centerx

        if self.is_active:
            if not self.is_exiting and not self.initial_descent_complete:
                self.descend_to_start_position()
            elif not self.is_exiting:
                # Fish will engage in chasing or avoiding behavior
                # Handle direction change and turning animation
                if player_on_left and self.current_direction != "left":
                    self.animate_turning("left")
                elif player_on_right and self.current_direction != "right":
                    self.animate_turning("right")
            elif self.is_exiting:
                # When exiting, continue ascending
                self.ascend_and_deactivate()

        self.rect.topleft = self.pos

        # Check for spawning and exiting conditions
        self.manage_spawn_and_exit()
        
    def animate_turning(self, new_direction):
        if not self.is_turning:
            self.image = self.images["spr_rainbow_fish_turning"]
            self.is_turning = True
            self.turning_timer = pygame.time.get_ticks() + RainbowFish.TURN_TIME_MS
        elif pygame.time.get_ticks() > self.turning_timer:
            # After turning animation, change to the new direction
            if new_direction == "left":
                self.image = self.images["spr_rainbow_fish_left"]
            elif new_direction == "right":
                self.image = self.images["spr_rainbow_fish_right"]
            self.current_direction = new_direction
            self.is_turning = False


    def decide_chase_or_avoid(self, player_size_score, player_star_power, player_pos):
        """
        Determine whether to chase or avoid the player based on the player's state
        and position.
        """
        # Only activate chasing or avoiding behavior if the fish is active and not exiting
        if self.is_active and not self.is_exiting:
            if self.size[0] - 45 <= player_size_score or player_star_power == 1:
                self.avoid_player(player_pos)
            else:
                self.chase_player(player_pos)

    def manage_spawn_and_exit(self):
        if self.rainbow_timer >= 2000 and not self.is_exiting:
            self.is_exiting = 1

    def ascend_and_deactivate(self):
        if self.pos[1] > -self.rect.height:
            self.pos = (self.pos[0], self.pos[1] - 3)
        else:
            self.reinitialize_for_next_spawn()
    
    def descend_to_start_position(self):
        self.arrow_warning_shown = 1
        if self.pos[1] < 200:
            self.pos = (self.pos[0], self.pos[1] + 2)
        else:
            self.arrow_warning_shown = 0
            self.initial_descent_complete = True

    def reinitialize_for_next_spawn(self):
        """
        Restart all variables for the next spawn cycle.
        """
        self.is_active = 0
        self.is_exiting = 0
        self.initial_descent_complete = False
        self.arrow_warning_shown = 0
        self.rainbow_timer = 0
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
        if self.size[0] < self.MAX_SIZE[0] and self.size[1] < self.MAX_SIZE[1]:
            self.size[0] += 10
            self.size[1] += 10
            self.size[0] = min(self.size[0], self.MAX_SIZE[0])
            self.size[1] = min(self.size[1], self.MAX_SIZE[1])
    
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
            self.is_exiting = 1
        elif(self.pos[1] < 32 or self.pos[1] > SCREEN_HEIGHT-32):
            self.is_exiting = 1
                
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
        self.is_active = 0
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
        if self.size[0]-20 <= 55: #increases till max size
            self.size[0] += 10
            self.size[1] += 10
    def collide_with_bright_blue_fish(self):
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
        self.rainbow_timer = 0
    def remove_sprite(self):
        self.kill()