import asyncio
import sys
import traceback

import pygame

from game_state import GameState
from high_score import HighScoreStore
from joystick import Joystick
from renderer import render_play_screen, render_ui_overlay
from runtime import ITCH_MODE
from utils import FPS, IMAGES, SCREEN_HEIGHT, SCREEN_WIDTH, TOP_UI_LAYER_HEIGHT

DEBUG = False
ZOOM_FACTOR = 1.5


class GameApp:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.pause_button_rect = pygame.Rect((SCREEN_WIDTH - 160, 3), (75, TOP_UI_LAYER_HEIGHT - 5))
        self.joystick = Joystick(IMAGES, screen)
        self.high_score_store = HighScoreStore(enabled=not ITCH_MODE)
        self.game_state = GameState(
            IMAGES,
            IMAGES["start_menu_bg"],
            IMAGES["info_screen_bg"],
            self.joystick,
            self.high_score_store,
        )
        self.zoomed_surface = pygame.Surface(
            (SCREEN_WIDTH // ZOOM_FACTOR, SCREEN_HEIGHT // ZOOM_FACTOR), pygame.SRCALPHA
        )
        self.background_y_first = 0
        self.background_y_second = -SCREEN_HEIGHT

    def _advance_background(self):
        self.background_y_first += 10
        self.background_y_second += 10

        if self.background_y_first >= SCREEN_HEIGHT:
            self.background_y_first = -SCREEN_HEIGHT
        if self.background_y_second >= SCREEN_HEIGHT:
            self.background_y_second = -SCREEN_HEIGHT

    def _get_camera(self):
        camera_x = max(
            0,
            min(
                self.game_state.player.rect.centerx - SCREEN_WIDTH // (2 * ZOOM_FACTOR),
                SCREEN_WIDTH - SCREEN_WIDTH // ZOOM_FACTOR,
            ),
        )
        camera_y = max(
            0,
            min(
                self.game_state.player.rect.centery - SCREEN_HEIGHT // (2 * ZOOM_FACTOR),
                SCREEN_HEIGHT - SCREEN_HEIGHT // ZOOM_FACTOR,
            ),
        )
        return camera_x, camera_y

    def _update_play_state(self):
        if self.game_state.is_paused:
            return

        self.game_state.rainbow_fish.player_size_score = self.game_state.player.size_score
        self.game_state.rainbow_fish.player_star_power = (
            self.game_state.player.star_power == self.game_state.player.INVINCIBLE_POWERUP
        )
        self.game_state.rainbow_fish.player_position = self.game_state.player.rect.center

        self.game_state.allsprites.update()
        self.game_state.arrow_warning_sprites.update()
        self.game_state.update(self.zoomed_surface)

        if self.game_state.rainbow_fish.is_active:
            self.game_state.rainbow_fish.decide_chase_or_avoid(
                self.game_state.player.size_score,
                self.game_state.player.star_power == self.game_state.player.INVINCIBLE_POWERUP,
                self.game_state.player.rect.center,
            )

    def _render_current_state(self):
        self.screen.fill((0, 0, 0))

        if self.game_state.current_state == GameState.INFO_SCREEN:
            self.game_state.show_info_screen(self.screen)
            return

        if self.game_state.current_state == GameState.START_SCREEN:
            self.game_state.show_start_screen(self.screen)
            return

        if self.game_state.current_state == GameState.GAME_OVER_SCREEN:
            self.game_state.show_game_over_screen(self.screen)
            return

        if self.game_state.current_state == GameState.PLAY_SCREEN:
            self._advance_background()
            camera_x, camera_y = self._get_camera()
            self._update_play_state()
            render_play_screen(
                self.screen,
                self.zoomed_surface,
                self.game_state,
                camera_x,
                camera_y,
                self.background_y_first,
                self.background_y_second,
                debug=DEBUG,
            )
            render_ui_overlay(self.screen, self.game_state, self.pause_button_rect, self.joystick)

    async def run(self):
        try:
            running = True
            while running:
                self.clock.tick(FPS)
                running = self.game_state.handle_input(self.pause_button_rect)
                if not running:
                    break

                self._render_current_state()
                pygame.display.update()
                await asyncio.sleep(0)
        except Exception:
            traceback.print_exc()
            error_lines = traceback.format_exc().splitlines()[-8:]
            error_font = pygame.font.SysFont("Courier", 18)
            while True:
                self.screen.fill((20, 0, 0))
                y = 20
                for line in ["Runtime error:"] + error_lines:
                    text = error_font.render(line[:110], True, (255, 255, 255))
                    self.screen.blit(text, (20, y))
                    y += 24
                pygame.display.update()
                await asyncio.sleep(0)
        finally:
            pygame.quit()
            if not ITCH_MODE:
                sys.exit()
