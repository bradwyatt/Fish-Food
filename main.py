import asyncio
import pygame
import os
import random
import sys
import datetime
import traceback
from utils import IMAGES, SOUNDS, FONTS, load_all_assets, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TOP_UI_LAYER_HEIGHT
from runtime import ITCH_MODE
from high_score import HighScoreStore
from shark import Shark
from red_fish import RedFish
from green_fish import GreenFish
from silver_fish import SilverFish
from snake import Snake
from bright_blue_fish import BrightBlueFish
from rainbow_fish import RainbowFish
from seahorse import Seahorse
from jellyfish import Jellyfish
from star_powerup import StarPowerup
from player import Player
from renderer import (
    render_game_over_screen,
    render_info_screen,
    render_play_screen,
    render_start_screen,
    render_ui_overlay,
)
import math


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fish Food")
gameicon = pygame.image.load("sprites/red_fish_ico.png")
pygame.display.set_icon(gameicon)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
DEBUG = False
ZOOM_FACTOR = 1.5 # Recommended to be 1.5
PLAY_AREA_LEFT = 32
PLAY_AREA_TOP = 32
PLAY_AREA_RIGHT = SCREEN_WIDTH - 32
PLAY_AREA_BOTTOM = SCREEN_HEIGHT - 64

def draw_text_button(screen, text, font, color, rect):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=rect.center)
    pygame.draw.rect(screen, (255, 127, 80), rect)  # Draw button rectangle
    screen.blit(text_surf, text_rect)
    return rect.collidepoint(pygame.mouse.get_pos())


def collide_rect_to_mask(sprite1, sprite2, mask_name='mask'):
    """
    Check for collision between sprite1's rect and a specified mask of sprite2.

    :param sprite1: The first sprite (uses its rect for collision).
    :param sprite2: The second sprite (whose specified mask is used for collision).
    :param mask_name: The name of the mask attribute in sprite2 to use for collision.
    :return: True if there is a collision, False otherwise.
    """
    # First, check if the rectangles collide. If not, there can't be a mask collision.
    if not pygame.sprite.collide_rect(sprite1, sprite2):
        return False

    # Create a temporary mask for sprite1's rect
    mask1 = pygame.mask.Mask((sprite1.rect.width, sprite1.rect.height))
    mask1.fill()  # Fill the mask (all pixels set to 1)

    # Get the specified mask from sprite2
    mask2 = getattr(sprite2, mask_name, None)
    if mask2 is None:
        raise ValueError(f"Mask '{mask_name}' not found in sprite2")

    # Get the offset between the two sprites
    offset_x = sprite2.rect.left - sprite1.rect.left
    offset_y = sprite2.rect.top - sprite1.rect.top

    # Use the offset to check if the masks overlap
    return mask1.overlap(mask2, (offset_x, offset_y)) is not None


def collide_mask_to_mask(sprite1, mask1_name, sprite2, mask2_name, use_rect_check=True):
    """
    Check for collision between two masks of two different sprites, with an optional
    rectangle collision check for optimization.

    :param sprite1: The first sprite.
    :param mask1_name: The name of the mask attribute in the first sprite.
    :param sprite2: The second sprite.
    :param mask2_name: The name of the mask attribute in the second sprite.
    :param use_rect_check: Whether to perform an initial rectangle collision check.
    :return: True if there is a collision, False otherwise.
    """
    # Retrieve the actual mask objects from the sprites
    mask1 = getattr(sprite1, mask1_name, None)
    mask2 = getattr(sprite2, mask2_name, None)

    # Ensure both masks are present
    if not mask1 or not mask2:
        return False

    # First, check if the rectangles collide if use_rect_check is True.
    if use_rect_check and not sprite1.rect.colliderect(sprite2.rect):
        return False

    # Calculate the offset between the two sprites
    offset_x = sprite2.rect.left - sprite1.rect.left
    offset_y = sprite2.rect.top - sprite1.rect.top

    # Check if the masks overlap
    return mask1.overlap(mask2, (offset_x, offset_y)) is not None


class Wall(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 0, 0, 0))  # Black color, can be changed to (0, 0, 0, 0) for invisible
        self.image.set_colorkey((0, 0, 0))  # Make black color transparent
        self.rect = self.image.get_rect()
    def remove_sprite(self):
        self.kill()

class Seaweed(pygame.sprite.Sprite):
    def __init__(self, allsprites, x_pos, y_pos):
        """
        Animated seaweed
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_seaweed"]
        self.rect = self.image.get_rect()
        self.rect.topleft = x_pos, y_pos
        allsprites.add(self)
        self.seaweed_animate_timer = random.randint(0, 30)
    def update(self):
        self.seaweed_animate_timer += 1
        seaweed_images = [IMAGES["spr_seaweed"], IMAGES["spr_seaweed_left"], IMAGES["spr_seaweed_right"]]
        if self.seaweed_animate_timer > 15 and self.seaweed_animate_timer < 30:
            self.image = seaweed_images[1]
        if self.seaweed_animate_timer >= 30:
            self.image = seaweed_images[2]
        if self.seaweed_animate_timer > 45:
            self.seaweed_animate_timer = 0
            self.image = seaweed_images[0]
    def remove_sprite(self):
        self.kill()

class ArrowWarning(pygame.sprite.Sprite):
    def __init__(self, arrow_warning_sprites, arrow_type, target_sprite, side='top'):
        pygame.sprite.Sprite.__init__(self)
        self.arrow_type = arrow_type
        self.image = IMAGES[f"arrow_warning_{arrow_type}_{side}"]  # e.g., "arrow_warning_red"
        self.rect = self.image.get_rect()
        self.target_sprite = target_sprite
        self.side = side

        # Adjust the position based on the side
        if side == 'top':
            self.rect.y = 40  # Fixed Y position for top
            self.rect.x = self.target_sprite.rect.left
        elif side == 'left':
            self.rect.x = SCREEN_WIDTH-100
            self.rect.y = self.target_sprite.rect.centery
        elif side == 'right':
            self.rect.x = 50
            self.rect.y = self.target_sprite.rect.centery

        arrow_warning_sprites.add(self)
        self.visible = False

    def update(self):
        if self.side == 'top':
            self.rect.x = self.target_sprite.rect.left
        elif self.side == 'left':
            self.rect.y = self.target_sprite.rect.centery
        elif self.side == 'right':
            self.rect.y = self.target_sprite.rect.centery
        
class GameState:
    START_SCREEN = 0
    PLAY_SCREEN = 1
    GAME_OVER_SCREEN = 2
    INFO_SCREEN = 3
    SCORE_BLIT_TICKS_TO_DISAPPEAR = 30
    TIMER_UNTIL_GAME_OVER_SCREEN = 100

    def __init__(self, images, start_screen_bg=None, info_screen_bg=None, joystick=None, high_score_store=None):
        self.allsprites = pygame.sprite.Group()
        self.arrow_warning_sprites = pygame.sprite.Group()
        self.score = 0
        self.score_blit = 0
        self.high_score_store = high_score_store or HighScoreStore(enabled=not ITCH_MODE)
        self.high_score_enabled = self.high_score_store.enabled
        self.high_score = self.high_score_store.load() if self.high_score_enabled else 0
        self.is_new_high_score = False
        self.key_states = {
            pygame.K_UP: False,
            pygame.K_LEFT: False,
            pygame.K_DOWN: False,
            pygame.K_RIGHT: False
        }
        self.current_state = GameState.START_SCREEN
        self.one_powerup_sound = 0
        self.score_disappear_timer = 0
        self.initialize_entities()
        self.start_screen_bg = start_screen_bg
        self.info_screen_bg = info_screen_bg
        self.is_paused = False
        self.joystick = joystick
        self.dead_fish_position = ()
        self.last_bbf_activation_score = 0  # Initialize last activation score for Bright Blue Fish
        self.game_over_timer = 0
        self.game_over_processed = False
        # Define button rectangles
        self.start_button_rect = pygame.Rect(400, 305, 200, 125)
        self.touch_position = None  # Position where the user touches the screen
        self.joystick_visible = False  # Whether the joystick is currently visible
        self.info_button_play_rect = pygame.Rect(SCREEN_WIDTH - 80, 3, 75, TOP_UI_LAYER_HEIGHT-5)  # Adjust position and size as needed


    def initialize_entities(self):
        # Initialize all your entities here
        self.player = Player(self.allsprites, IMAGES)
        self.walls = []
        self.seaweeds = []
        for x_top in range(31):
            self.wall = Wall(self.allsprites)
            self.wall.rect.topleft = (x_top*32, 0) #top walls
            self.walls.append(self.wall)
        for x_bottom in range(32, SCREEN_WIDTH-32, 32):
            self.wall = Wall(self.allsprites)
            self.wall.rect.topleft = (x_bottom, SCREEN_HEIGHT-32) #bottom walls
            self.walls.append(self.wall)
        for y_left in range(0, SCREEN_HEIGHT-32, 32):
            self.wall = Wall(self.allsprites)
            self.wall.rect.topleft = (0, y_left) #left walls
            self.walls.append(self.wall)
        for y_right in range(0, SCREEN_HEIGHT-32, 32):
            self.wall = Wall(self.allsprites)
            self.wall.rect.topleft = (SCREEN_WIDTH-32, y_right) #right walls
            self.walls.append(self.wall)
        for x_pos in range(150, SCREEN_WIDTH-165, 60):
            self.seaweed = Seaweed(self.allsprites, x_pos, SCREEN_HEIGHT-200)
            self.seaweeds.append(self.seaweed)
        self.red_fishes = [RedFish(self.allsprites, IMAGES) for i in range(6)]
        self.green_fishes = [GreenFish(self.allsprites, IMAGES) for i in range(3)]
        self.silver_fish = SilverFish(self.allsprites, IMAGES)
        self.snake = Snake(self.allsprites, IMAGES)
        self.seahorse = Seahorse(self.allsprites, IMAGES)
        self.jellyfishes = [Jellyfish(self.allsprites, IMAGES) for i in range(len(Jellyfish.JELLYFISHES_SCORE_TO_SPAWN))]
        self.sharks = []
        self.silver_arrow_warnings = []
        for s in range(len(Shark.SHARKS_SCORES_TO_SPAWN)):
            self.sharks.append(Shark(self.allsprites, IMAGES))
            self.silver_arrow_warnings.append(ArrowWarning(self.arrow_warning_sprites, "silver", self.sharks[s]))
        self.star = StarPowerup(self.allsprites, IMAGES)
        self.rainbow_fish = RainbowFish(self.allsprites, IMAGES)
        self.red_arrow_warning = ArrowWarning(self.arrow_warning_sprites, "red", self.rainbow_fish)
        self.bright_blue_fish = BrightBlueFish(self.allsprites, IMAGES)
        self.blue_arrow_warning_left = ArrowWarning(self.arrow_warning_sprites, "blue", self.bright_blue_fish, "left")
        self.blue_arrow_warning_right = ArrowWarning(self.arrow_warning_sprites, "blue", self.bright_blue_fish, "right")

        
    def reset_game(self, images):
        self.allsprites.empty()
        self.arrow_warning_sprites.empty()
        self.current_state = GameState.PLAY_SCREEN
        self.score = 0
        self.initialize_entities()
        self.player.last_pressed = 0
        self.key_states = {
            pygame.K_UP: False,
            pygame.K_LEFT: False,
            pygame.K_DOWN: False,
            pygame.K_RIGHT: False
        }
        self.last_bbf_activation_score = 0
        self.game_over_timer = 0
        self.game_over_processed = False
        self.is_new_high_score = False
    
    def change_state(self, new_state):
        self.current_state = new_state

    def finalize_high_score(self):
        if not self.high_score_enabled:
            return False

        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_store.save(self.high_score)
            return True

        return False


    def activate_game_objects(self, zoomed_surface):
        # Rainbow Fish activation logic
        if self.rainbow_fish.rainbow_timer >= RainbowFish.NUM_OF_TICKS_FOR_ENTRANCE:
            self.rainbow_fish.is_active = True
        if self.rainbow_fish.is_active and not self.rainbow_fish.initial_descent_complete:
            if self.red_arrow_warning.visible == False:
                # Only play the sound right before the arrow shows up
                SOUNDS["snd_shark_incoming"].play()
            self.red_arrow_warning.visible = True
        else:
            self.red_arrow_warning.visible = False
        # Sharks
        for s in range(len(Shark.SHARKS_SCORES_TO_SPAWN)):
            if self.score >= Shark.SHARKS_SCORES_TO_SPAWN[s]:
                self.sharks[s].activate = True
                if self.sharks[s].activate and not self.sharks[s].initial_descent_complete:
                    if self.silver_arrow_warnings[s].visible == False and self.sharks[s].mini_shark == False:
                        SOUNDS["snd_shark_incoming"].play()
                    self.silver_arrow_warnings[s].visible = True
                else:
                    self.silver_arrow_warnings[s].visible = False
        # Bright Blue Fish
        if self.bright_blue_fish.activate and not self.bright_blue_fish.lateral_entry_complete:
            SOUNDS["snd_siren"].play()
            if self.bright_blue_fish.direction == BrightBlueFish.DIR_RIGHT:
                # Position the blue arrow on the left side of the screen
                self.blue_arrow_warning_right.visible = True
            elif self.bright_blue_fish.direction == BrightBlueFish.DIR_LEFT:
                # Position the blue arrow on the right side of the screen
                self.blue_arrow_warning_left.visible = True
        else:
            self.blue_arrow_warning_right.visible = False
            self.blue_arrow_warning_left.visible = False
        # Jellyfish
        for j in range(len(Jellyfish.JELLYFISHES_SCORE_TO_SPAWN)):
            if self.score >= Jellyfish.JELLYFISHES_SCORE_TO_SPAWN[j]:
                self.jellyfishes[j].activate = True
                
    def player_eat_prey_collision(self, prey, snd="snd_eat"):
        self.player.collide_with_prey()
        SOUNDS[snd].play()
        self.dead_fish_position = prey.rect.topleft
        fish_score = prey.get_score_value()
        self.score += fish_score
        self.score_blit = fish_score
        if self.player.size_score >= self.player.MAX_SIZE_SCORE:
            self.player.size_score = self.player.MAX_SIZE_SCORE
        else:
            self.player.size_score += fish_score
        prey.collide_with_player()
        
    def predator_eat_player_collision(self, enemy_object):
        self.player.game_over = True
        enemy_object.game_over = True

    def _is_outside_play_area(self, rect):
        return (
            rect.left < PLAY_AREA_LEFT
            or rect.right > PLAY_AREA_RIGHT
            or rect.top < PLAY_AREA_TOP
            or rect.bottom > PLAY_AREA_BOTTOM
        )

    def _handle_red_fish_boundary(self, red_fish):
        if self._is_outside_play_area(red_fish.rect):
            red_fish.change_dir_timer = 0
            red_fish.bounce_off_walls()

    def _handle_green_fish_boundary(self, green_fish):
        if self._is_outside_play_area(green_fish.rect):
            green_fish.change_direction()
            green_fish.move_away_from_wall(None)

    def _handle_shark_boundary(self, shark):
        if shark.activate and shark.initial_descent_complete and self._is_outside_play_area(shark.rect):
            shark.update_direction()
            shark.stop_timer = pygame.time.get_ticks() + Shark.TURN_TIME_MS
            shark.offset_from_wall()

    def _restart_powerup_timer_sound(self):
        pygame.mixer.stop()
        SOUNDS["snd_powerup_timer"].play()

    def _handle_powerup_collision(self, powerup_sprite, collected_sound_key, on_collect, restart_timer_sound=True):
        on_collect()
        powerup_sprite.collide_with_player()
        SOUNDS[collected_sound_key].play()
        self.one_powerup_sound += 1
        if restart_timer_sound:
            self._restart_powerup_timer_sound()

    def handle_collisions(self):
        self._check_prey_collisions()
        self._check_predator_collisions()
        self._check_hazard_collisions()
        self._check_powerup_collisions()

    def _check_prey_collisions(self):
        for red_fish in self.red_fishes:
            if self.player.star_power == self.player.INVINCIBLE_POWERUP:
                if collide_rect_to_mask(red_fish, self.player, "body_mask"):
                    self.player_eat_prey_collision(red_fish)
            else:
                if collide_rect_to_mask(red_fish, self.player, "face_mask"):
                    self.player_eat_prey_collision(red_fish)
            for green_fish in self.green_fishes:
                if red_fish.rect.colliderect(green_fish):
                    green_fish.collision_with_red_fish()
                    if green_fish.is_big == False:
                        red_fish.collide_with_green_fish()
            if pygame.sprite.collide_mask(red_fish, self.bright_blue_fish):
                red_fish.collide_with_bright_blue_fish()
            self._handle_red_fish_boundary(red_fish)

        for green_fish in self.green_fishes:
            if(green_fish.is_big == False or 
               self.player.size_score >= Player.PLAYER_SCORE_BIGGER_THAN_BIG_GREEN_FISH or 
               self.player.star_power == Player.INVINCIBLE_POWERUP):
                if self.player.star_power == self.player.INVINCIBLE_POWERUP:
                    if collide_mask_to_mask(green_fish, "body_mask", self.player, "body_mask", False):
                        self.player_eat_prey_collision(green_fish)
                else:
                    if collide_mask_to_mask(green_fish, "body_mask", self.player, "face_mask", False):
                        # Green fish is small or player is bigger than green fish or player has star power
                        self.player_eat_prey_collision(green_fish)
            else: 
                if collide_mask_to_mask(green_fish, "face_mask", self.player, "body_mask", False):
                    if green_fish.is_big:
                        # Green fish is bigger than player
                        self.predator_eat_player_collision(green_fish)
            if pygame.sprite.collide_mask(green_fish, self.bright_blue_fish):
                green_fish.reset_position()
            self._handle_green_fish_boundary(green_fish)

        if self.player.star_power == self.player.INVINCIBLE_POWERUP:
            if collide_rect_to_mask(self.silver_fish, self.player, "body_mask"):
                self.player_eat_prey_collision(self.silver_fish)
        else:
            if collide_rect_to_mask(self.silver_fish, self.player, "face_mask"):
                self.player_eat_prey_collision(self.silver_fish)

        if pygame.sprite.collide_mask(self.silver_fish, self.bright_blue_fish):
            SOUNDS["snd_eat"].play()
            self.silver_fish.collide_with_bright_blue_fish()

        if pygame.sprite.collide_mask(self.rainbow_fish, self.player):
            # Player eats rainbow_fish only when appears bigger (arbitrary)
            if (self.rainbow_fish.size_score <= self.player.size_score or 
                self.player.star_power == self.player.INVINCIBLE_POWERUP):
                self.player_eat_prey_collision(self.rainbow_fish)
            else:
                if self.player.star_power != Player.INVINCIBLE_POWERUP:
                    self.predator_eat_player_collision(self.rainbow_fish)

        if pygame.sprite.collide_mask(self.rainbow_fish, self.bright_blue_fish):
            SOUNDS["snd_eat"].play()
            self.rainbow_fish.collide_with_bright_blue_fish()

    def _check_predator_collisions(self):
        if collide_mask_to_mask(self.bright_blue_fish, "mask", self.player, "body_mask"):
            if self.player.star_power != Player.INVINCIBLE_POWERUP:
                self.predator_eat_player_collision(self.bright_blue_fish)

        for shark in self.sharks:
            if self.player.star_power == Player.SHARK_SHRINKER_POWERUP:
                shark.mini_shark = True
                if collide_mask_to_mask(self.player, "face_mask", shark, "mask", False):
                    self.player_eat_prey_collision(shark, "snd_eat_shark")
            elif self.player.star_power == Player.INVINCIBLE_POWERUP:
                pass
            else:
                shark.mini_shark = False
                if collide_mask_to_mask(self.player, "body_mask", shark, "mask", False):
                    self.predator_eat_player_collision(shark)
            if pygame.sprite.collide_mask(shark, self.bright_blue_fish):
                shark.collide_with_bright_blue_fish()
                SOUNDS["snd_eat"].play()
            self._handle_shark_boundary(shark)

    def _check_hazard_collisions(self):
        if pygame.sprite.collide_mask(self.snake, self.player):
            self.snake.collide_with_player()
            if self.player.star_power != Player.INVINCIBLE_POWERUP:
                self.player.collide_with_snake()
                SOUNDS["snd_size_down"].play()
            else:
                SOUNDS["snd_eat"].play()

        if pygame.sprite.collide_mask(self.snake, self.bright_blue_fish):
            self.snake.collide_with_bright_blue_fish()

        for jellyfish in self.jellyfishes:
            if pygame.sprite.collide_mask(jellyfish, self.player):
                if self.player.star_power == Player.INVINCIBLE_POWERUP:
                    jellyfish.collide_with_player()
                    SOUNDS["snd_eat"].play()
                else:
                    self._handle_powerup_collision(
                        jellyfish,
                        "snd_size_down",
                        self.player.collide_with_jellyfish,
                    )
            if pygame.sprite.collide_mask(jellyfish, self.bright_blue_fish):
                jellyfish.collide_with_bright_blue_fish()
                SOUNDS["snd_eat"].play()

    def _check_powerup_collisions(self):
        if pygame.sprite.collide_mask(self.seahorse, self.player):
            self._handle_powerup_collision(self.seahorse, "snd_eat", self.player.collide_with_seahorse)

        if self.player.rect.colliderect(self.star):
            self._handle_powerup_collision(self.star, "snd_eat", self.player.collide_with_star)

                
    def handle_input(self, pause_button_rect):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
    
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_states:
                    self.key_states[event.key] = True
    
            if event.type == pygame.KEYUP:
                if event.key in self.key_states:
                    self.key_states[event.key] = False
                    
            if self.current_state == GameState.GAME_OVER_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.reset_game(IMAGES)
            elif self.current_state == GameState.START_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button_rect.collidepoint(event.pos):
                        self.change_state(GameState.INFO_SCREEN)
            elif self.current_state == GameState.INFO_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Clicking anywhere on the Info screen returns to the Start screen
                    self.change_state(GameState.PLAY_SCREEN)
            elif self.current_state == GameState.PLAY_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_button_rect.collidepoint(event.pos):
                        self.is_paused = not self.is_paused
                    elif self.info_button_play_rect.collidepoint(event.pos):
                        self.is_paused = True
                        self.change_state(GameState.INFO_SCREEN)
                    else:
                        # Call the joystick's handle_click method
                        self.joystick.handle_click(event.pos)
        
                if event.type == pygame.MOUSEMOTION:
                    if self.joystick.mouse_is_pressed:
                        new_direction = self.joystick.handle_mouse_move(event.pos)
                        if new_direction:
                            if new_direction == "neutral":
                                for key in self.key_states:
                                    self.key_states[key] = False
                            else:
                                for key in self.key_states:
                                    self.key_states[key] = False
                                for key in self.map_direction_to_key(new_direction):
                                    self.key_states[key] = True

                if event.type == pygame.MOUSEBUTTONUP:
                    # Call the joystick's handle_mouse_up method
                    self.joystick.handle_mouse_up()
        return True
                        
    def map_direction_to_key(self, direction):
        mapping = {
            "up": [pygame.K_UP],
            "up_right": [pygame.K_UP, pygame.K_RIGHT],
            "right": [pygame.K_RIGHT],
            "down_right": [pygame.K_DOWN, pygame.K_RIGHT],
            "down": [pygame.K_DOWN],
            "down_left": [pygame.K_DOWN, pygame.K_LEFT],
            "left": [pygame.K_LEFT],
            "up_left": [pygame.K_UP, pygame.K_LEFT]
        }
        return mapping.get(direction, [])


                    
    def show_start_screen(self, screen):
        render_start_screen(
            screen,
            self.start_screen_bg,
            self.start_button_rect,
            self.high_score_enabled,
            self.high_score,
        )

    def show_info_screen(self, screen):
        render_info_screen(screen, self.info_screen_bg)

    def show_game_over_screen(self, screen):
        render_game_over_screen(
            screen,
            self.score,
            self.high_score_enabled,
            self.high_score,
            self.is_new_high_score,
        )


    def update(self, zoomed_surface):
        if self.player.game_over == True:
            # Fades player when predator eats it
            self.game_over_timer += 1
            if self.game_over_timer >= self.TIMER_UNTIL_GAME_OVER_SCREEN and not self.game_over_processed:
                self.is_new_high_score = self.finalize_high_score()
                self.game_over_processed = True
                self.current_state = self.GAME_OVER_SCREEN
        elif self.current_state == GameState.PLAY_SCREEN and not self.is_paused:
            self.handle_collisions()
            self.activate_game_objects(zoomed_surface)
            move_direction = None
            if self.key_states[pygame.K_UP] and self.key_states[pygame.K_RIGHT]:
                move_direction = "up_right"
            elif self.key_states[pygame.K_UP] and self.key_states[pygame.K_LEFT]:
                move_direction = "up_left"
            elif self.key_states[pygame.K_DOWN] and self.key_states[pygame.K_RIGHT]:
                move_direction = "down_right"
            elif self.key_states[pygame.K_DOWN] and self.key_states[pygame.K_LEFT]:
                move_direction = "down_left"
            elif self.key_states[pygame.K_UP]:
                move_direction = "up"
            elif self.key_states[pygame.K_DOWN]:
                move_direction = "down"
            elif self.key_states[pygame.K_LEFT]:
                move_direction = "left"
            elif self.key_states[pygame.K_RIGHT]:
                move_direction = "right"

            if move_direction:
                self.player.move(move_direction)
        
            # Stop movement if no arrow keys are pressed
            if not any(self.key_states.values()):
                self.player.stop_movement()
                
            # Activate Bright Blue Fish every time the score increases by increments
            if self.bright_blue_fish.try_activate(self.score, self.last_bbf_activation_score):
                self.last_bbf_activation_score = self.score


class Joystick:
    def __init__(self, images, screen):
        self.images = images
        self.screen = screen
        self.pressed_direction = None  # To track the currently pressed direction        
        self.neutral_zone_rect = images['spr_neutral_zone'].get_rect(center=(158, SCREEN_HEIGHT - 143))
        # Define the positions and sizes of the arrows
        self.arrows = {
            "up_left": self.images["spr_unpressed_arrow_up_left"].get_rect(topleft=(20, SCREEN_HEIGHT - 280)),
            "up_right": self.images["spr_unpressed_arrow_up_right"].get_rect(topleft=(200, SCREEN_HEIGHT - 280)),
            "down_left": self.images["spr_unpressed_arrow_down_left"].get_rect(topleft=(20, SCREEN_HEIGHT - 100)),
            "down_right": self.images["spr_unpressed_arrow_down_right"].get_rect(topleft=(200, SCREEN_HEIGHT - 100)),
            "up": self.images["spr_unpressed_arrow_up"].get_rect(topleft=(110, SCREEN_HEIGHT - 280)),
            "down": self.images["spr_unpressed_arrow_down"].get_rect(topleft=(110, SCREEN_HEIGHT - 100)),
            "left": self.images["spr_unpressed_arrow_left"].get_rect(topleft=(20, SCREEN_HEIGHT - 190)),
            "right": self.images["spr_unpressed_arrow_right"].get_rect(topleft=(200, SCREEN_HEIGHT - 190))
        }
        
        # Mapping of keyboard keys to joystick directions
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
        self.activation_distance = 30  # The distance in pixels to activate direction change
        self.center_position = None  # Initialize the center position


    
    def draw(self, key_states, center_position):
        if center_position is None:
            return  # Don't draw if there's no center position

        # Calculate the top-left position for the neutral zone
        neutral_zone_size = self.images['spr_neutral_zone'].get_size()
        neutral_zone_top_left = (center_position[0] - neutral_zone_size[0] // 2,
                                 center_position[1] - neutral_zone_size[1] // 2)

        # Draw neutral zone centered at the mouse click position
        self.screen.blit(self.images['spr_neutral_zone'], neutral_zone_top_left)

        # Calculate and draw arrows around the neutral zone
        arrow_offsets = {
            "up": (0, -neutral_zone_size[1]),
            "down": (0, neutral_zone_size[1]),
            "left": (-neutral_zone_size[0], 0),
            "right": (neutral_zone_size[0], 0),
            # Add other directions (diagonals) here with appropriate offsets
        }
        for direction, offset in arrow_offsets.items():
            arrow_image_key = f"spr_{'pressed' if key_states.get(self.map_direction_to_key(direction), False) else 'unpressed'}_arrow_{direction}"
            arrow_image = self.images[arrow_image_key]
            arrow_rect = arrow_image.get_rect(center=(center_position[0] + offset[0], center_position[1] + offset[1]))
            self.screen.blit(arrow_image, arrow_rect.topleft)
            
    @staticmethod
    def map_direction_to_key(direction):
        direction_to_key = {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            # Add mappings for other directions (diagonals) here
        }
        return direction_to_key.get(direction, None)


    def blit_arrow(self, direction, is_pressed):
        image_key = "spr_pressed_arrow_" if is_pressed else "spr_unpressed_arrow_"
        image_key += direction
        rect = self.arrows[direction]
        self.screen.blit(self.images[image_key], rect.topleft)

    def handle_click(self, mouse_pos):
        # Check if the click is within any of the joystick areas
        self.center_position = mouse_pos  # Set the center position when mouse is pressed

        if self.neutral_zone_rect.collidepoint(mouse_pos):
            self.pressed_direction = "neutral"
        else:
            for direction, rect in self.arrows.items():
                if rect.collidepoint(mouse_pos):
                    self.pressed_direction = direction
                    break

        self.mouse_is_pressed = True  # Set the flag when the mouse is pressed
        return self.pressed_direction
    
    def handle_mouse_up(self):
        self.center_position = None  # Reset the center position when mouse is released
        # Return the last pressed direction when the mouse button is released
        last_direction = self.pressed_direction
        self.mouse_is_pressed = False  # Reset the flag when the mouse is released
        self.pressed_direction = None  # Reset the pressed direction
        return last_direction
        
    def handle_mouse_move(self, mouse_pos):
        if not self.mouse_is_pressed or self.center_position is None:
            return None

        # Calculate distance and angle from the joystick center
        dx = mouse_pos[0] - self.center_position[0]
        dy = mouse_pos[1] - self.center_position[1]
        distance = math.sqrt(dx**2 + dy**2)
        angle = math.degrees(math.atan2(-dy, dx)) % 360  # Negative dy because screen coordinates are inverted on y-axis

        # Determine the direction based on the angle
        if distance > self.activation_distance:  # Only change direction if the mouse is dragged far enough
            if 45 <= angle < 135:
                return "up"
            elif 135 <= angle < 225:
                return "left"
            elif 225 <= angle < 315:
                return "down"
            else:
                return "right"
        else:
            return "neutral"

def zoom_in_on_player(screen, player, ZOOM_FACTOR):
    # Define the area around the player to zoom in on
    zoom_width, zoom_height = 100, 100  # Adjust size as needed
    zoom_rect = pygame.Rect(
        player.rect.centerx - zoom_width // 2,
        player.rect.centery - zoom_height // 2,
        zoom_width,
        zoom_height
    )

    # Ensure the zoom rectangle doesn't go outside the screen
    zoom_rect.clamp_ip(screen.get_rect())

    # Capture the area around the player
    subsurface = screen.subsurface(zoom_rect)

    # Scale up the captured area
    zoomed_surface = pygame.transform.scale(
        subsurface,
        (zoom_rect.width * ZOOM_FACTOR, zoom_rect.height * ZOOM_FACTOR)
    )

    return zoomed_surface

# Main game loop
async def main():
    try:
        pause_button_size = (75, TOP_UI_LAYER_HEIGHT-5)
        button_color = (255, 255, 255)
        pause_button_position = (SCREEN_WIDTH - 160, 3)
        pause_button_rect = pygame.Rect(pause_button_position, pause_button_size)

        (x_first, y_first) = (0, 0)
        (x_second, y_second) = (0, -SCREEN_HEIGHT)
        load_all_assets()

        running = True
        joystick = Joystick(IMAGES, screen)
        high_score_store = HighScoreStore(enabled=not ITCH_MODE)
        game_state_manager = GameState(
            IMAGES,
            IMAGES['start_menu_bg'],
            IMAGES['info_screen_bg'],
            joystick,
            high_score_store,
        )
        zoomed_surface = pygame.Surface((SCREEN_WIDTH // ZOOM_FACTOR, SCREEN_HEIGHT // ZOOM_FACTOR), pygame.SRCALPHA)

        world_width = SCREEN_WIDTH
        world_height = SCREEN_HEIGHT

        while running:
            clock.tick(FPS)
            running = game_state_manager.handle_input(pause_button_rect)
            if not running:
                break
            screen.fill((0, 0, 0))

            if game_state_manager.current_state == GameState.INFO_SCREEN:
                game_state_manager.show_info_screen(screen)
            elif game_state_manager.current_state == GameState.START_SCREEN:
                game_state_manager.show_start_screen(screen)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
            elif game_state_manager.current_state == GameState.GAME_OVER_SCREEN:
                game_state_manager.show_game_over_screen(screen)
            elif game_state_manager.current_state == GameState.PLAY_SCREEN:
                y_first += 10
                y_second += 10

                if y_first >= SCREEN_HEIGHT:
                    y_first = -SCREEN_HEIGHT
                if y_second >= SCREEN_HEIGHT:
                    y_second = -SCREEN_HEIGHT

                camera_x = max(
                    0,
                    min(
                        game_state_manager.player.rect.centerx - SCREEN_WIDTH // (2 * ZOOM_FACTOR),
                        world_width - SCREEN_WIDTH // ZOOM_FACTOR,
                    ),
                )
                camera_y = max(
                    0,
                    min(
                        game_state_manager.player.rect.centery - SCREEN_HEIGHT // (2 * ZOOM_FACTOR),
                        world_height - SCREEN_HEIGHT // ZOOM_FACTOR,
                    ),
                )

                if not game_state_manager.is_paused:
                    game_state_manager.rainbow_fish.player_size_score = game_state_manager.player.size_score
                    game_state_manager.rainbow_fish.player_star_power = (
                        game_state_manager.player.star_power == game_state_manager.player.INVINCIBLE_POWERUP
                    )
                    game_state_manager.rainbow_fish.player_position = game_state_manager.player.rect.center

                    game_state_manager.allsprites.update()
                    game_state_manager.arrow_warning_sprites.update()
                    game_state_manager.update(zoomed_surface)

                    if game_state_manager.rainbow_fish.is_active:
                        game_state_manager.rainbow_fish.decide_chase_or_avoid(
                            game_state_manager.player.size_score,
                            game_state_manager.player.star_power == game_state_manager.player.INVINCIBLE_POWERUP,
                            game_state_manager.player.rect.center,
                        )

                render_play_screen(
                    screen,
                    zoomed_surface,
                    game_state_manager,
                    camera_x,
                    camera_y,
                    y_first,
                    y_second,
                    debug=DEBUG,
                )
                render_ui_overlay(screen, game_state_manager, pause_button_rect, joystick)

            pygame.display.update()
            await asyncio.sleep(0)
    except Exception:
        traceback.print_exc()
        error_lines = traceback.format_exc().splitlines()[-8:]
        error_font = pygame.font.SysFont("Courier", 18)
        while True:
            screen.fill((20, 0, 0))
            y = 20
            for line in ["Runtime error:"] + error_lines:
                text = error_font.render(line[:110], True, (255, 255, 255))
                screen.blit(text, (20, y))
                y += 24
            pygame.display.update()
            await asyncio.sleep(0)
    finally:
        pygame.quit()
        if not ITCH_MODE:
            sys.exit()

# Run the game
asyncio.run(main())
