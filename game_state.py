import pygame

from bright_blue_fish import BrightBlueFish
from collisions import collide_mask_to_mask, collide_rect_to_mask
from game_factory import build_game_entities
from high_score import HighScoreStore
from jellyfish import Jellyfish
from player import Player
from rainbow_fish import RainbowFish
from renderer import render_game_over_screen, render_info_screen, render_start_screen
from runtime import ITCH_MODE
from shark import Shark
from utils import IMAGES, SCREEN_HEIGHT, SCREEN_WIDTH, SOUNDS, TOP_UI_LAYER_HEIGHT

PLAY_AREA_LEFT = 32
PLAY_AREA_TOP = 32
PLAY_AREA_RIGHT = SCREEN_WIDTH - 32
PLAY_AREA_BOTTOM = SCREEN_HEIGHT - 64


class GameState:
    START_SCREEN = 0
    PLAY_SCREEN = 1
    GAME_OVER_SCREEN = 2
    INFO_SCREEN = 3
    SCORE_BLIT_TICKS_TO_DISAPPEAR = 30
    TIMER_UNTIL_GAME_OVER_SCREEN = 100

    def __init__(self, images, start_screen_bg=None, info_screen_bg=None, joystick=None, high_score_store=None):
        self.images = images
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
            pygame.K_RIGHT: False,
        }
        self.current_state = GameState.START_SCREEN
        self.one_powerup_sound = 0
        self.score_disappear_timer = 0
        self.start_screen_bg = start_screen_bg
        self.info_screen_bg = info_screen_bg
        self.is_paused = False
        self.joystick = joystick
        self.dead_fish_position = ()
        self.last_bbf_activation_score = 0
        self.game_over_timer = 0
        self.game_over_processed = False
        self.start_button_rect = pygame.Rect(400, 305, 200, 125)
        self.touch_position = None
        self.joystick_visible = False
        self.info_button_play_rect = pygame.Rect(SCREEN_WIDTH - 80, 3, 75, TOP_UI_LAYER_HEIGHT - 5)
        self.initialize_entities()

    def initialize_entities(self):
        build_game_entities(self)

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
            pygame.K_RIGHT: False,
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
        if self.rainbow_fish.rainbow_timer >= RainbowFish.NUM_OF_TICKS_FOR_ENTRANCE:
            self.rainbow_fish.is_active = True
        if self.rainbow_fish.is_active and not self.rainbow_fish.initial_descent_complete:
            if self.red_arrow_warning.visible is False:
                SOUNDS["snd_shark_incoming"].play()
            self.red_arrow_warning.visible = True
        else:
            self.red_arrow_warning.visible = False

        for s in range(len(Shark.SHARKS_SCORES_TO_SPAWN)):
            if self.score >= Shark.SHARKS_SCORES_TO_SPAWN[s]:
                self.sharks[s].activate = True
                if self.sharks[s].activate and not self.sharks[s].initial_descent_complete:
                    if self.silver_arrow_warnings[s].visible is False and self.sharks[s].mini_shark is False:
                        SOUNDS["snd_shark_incoming"].play()
                    self.silver_arrow_warnings[s].visible = True
                else:
                    self.silver_arrow_warnings[s].visible = False

        if self.bright_blue_fish.activate and not self.bright_blue_fish.lateral_entry_complete:
            SOUNDS["snd_siren"].play()
            if self.bright_blue_fish.direction == BrightBlueFish.DIR_RIGHT:
                self.blue_arrow_warning_right.visible = True
            elif self.bright_blue_fish.direction == BrightBlueFish.DIR_LEFT:
                self.blue_arrow_warning_left.visible = True
        else:
            self.blue_arrow_warning_right.visible = False
            self.blue_arrow_warning_left.visible = False

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
                    if green_fish.is_big is False:
                        red_fish.collide_with_green_fish()
            if pygame.sprite.collide_mask(red_fish, self.bright_blue_fish):
                red_fish.collide_with_bright_blue_fish()
            self._handle_red_fish_boundary(red_fish)

        for green_fish in self.green_fishes:
            if (
                green_fish.is_big is False
                or self.player.size_score >= Player.PLAYER_SCORE_BIGGER_THAN_BIG_GREEN_FISH
                or self.player.star_power == Player.INVINCIBLE_POWERUP
            ):
                if self.player.star_power == self.player.INVINCIBLE_POWERUP:
                    if collide_mask_to_mask(green_fish, "body_mask", self.player, "body_mask", False):
                        self.player_eat_prey_collision(green_fish)
                else:
                    if collide_mask_to_mask(green_fish, "body_mask", self.player, "face_mask", False):
                        self.player_eat_prey_collision(green_fish)
            else:
                if collide_mask_to_mask(green_fish, "face_mask", self.player, "body_mask", False):
                    if green_fish.is_big:
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
            if self.rainbow_fish.size_score <= self.player.size_score or self.player.star_power == Player.INVINCIBLE_POWERUP:
                self.player_eat_prey_collision(self.rainbow_fish)
            elif self.player.star_power != Player.INVINCIBLE_POWERUP:
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

            if event.type == pygame.KEYDOWN and event.key in self.key_states:
                self.key_states[event.key] = True

            if event.type == pygame.KEYUP and event.key in self.key_states:
                self.key_states[event.key] = False

            if self.current_state == GameState.GAME_OVER_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.reset_game(IMAGES)
            elif self.current_state == GameState.START_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN and self.start_button_rect.collidepoint(event.pos):
                    self.change_state(GameState.INFO_SCREEN)
            elif self.current_state == GameState.INFO_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.change_state(GameState.PLAY_SCREEN)
            elif self.current_state == GameState.PLAY_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_button_rect.collidepoint(event.pos):
                        self.is_paused = not self.is_paused
                    elif self.info_button_play_rect.collidepoint(event.pos):
                        self.is_paused = True
                        self.change_state(GameState.INFO_SCREEN)
                    elif self.joystick is not None:
                        self.joystick.handle_click(event.pos)

                if event.type == pygame.MOUSEMOTION and self.joystick is not None:
                    if self.joystick.mouse_is_pressed:
                        new_direction = self.joystick.handle_mouse_move(event.pos)
                        if new_direction:
                            for key in self.key_states:
                                self.key_states[key] = False
                            if new_direction != "neutral":
                                for key in self.map_direction_to_key(new_direction):
                                    self.key_states[key] = True

                if event.type == pygame.MOUSEBUTTONUP and self.joystick is not None:
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
            "up_left": [pygame.K_UP, pygame.K_LEFT],
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
        if self.player.game_over is True:
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

            if not any(self.key_states.values()):
                self.player.stop_movement()

            if self.bright_blue_fish.try_activate(self.score, self.last_bbf_activation_score):
                self.last_bbf_activation_score = self.score
