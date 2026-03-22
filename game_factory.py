from arrow_warning import ArrowWarning
from bright_blue_fish import BrightBlueFish
from green_fish import GreenFish
from jellyfish import Jellyfish
from player import Player
from rainbow_fish import RainbowFish
from red_fish import RedFish
from seahorse import Seahorse
from seaweed import Seaweed
from shark import Shark
from silver_fish import SilverFish
from snake import Snake
from star_powerup import StarPowerup
from utils import SCREEN_HEIGHT, SCREEN_WIDTH
from wall import Wall


def build_game_entities(game_state):
    game_state.player = Player(game_state.allsprites, game_state.images)
    game_state.walls = []
    game_state.seaweeds = []

    for x_top in range(31):
        wall = Wall(game_state.allsprites)
        wall.rect.topleft = (x_top * 32, 0)
        game_state.walls.append(wall)

    for x_bottom in range(32, SCREEN_WIDTH - 32, 32):
        wall = Wall(game_state.allsprites)
        wall.rect.topleft = (x_bottom, SCREEN_HEIGHT - 32)
        game_state.walls.append(wall)

    for y_left in range(0, SCREEN_HEIGHT - 32, 32):
        wall = Wall(game_state.allsprites)
        wall.rect.topleft = (0, y_left)
        game_state.walls.append(wall)

    for y_right in range(0, SCREEN_HEIGHT - 32, 32):
        wall = Wall(game_state.allsprites)
        wall.rect.topleft = (SCREEN_WIDTH - 32, y_right)
        game_state.walls.append(wall)

    for x_pos in range(150, SCREEN_WIDTH - 165, 60):
        seaweed = Seaweed(game_state.allsprites, x_pos, SCREEN_HEIGHT - 200)
        game_state.seaweeds.append(seaweed)

    game_state.red_fishes = [RedFish(game_state.allsprites, game_state.images) for _ in range(6)]
    game_state.green_fishes = [GreenFish(game_state.allsprites, game_state.images) for _ in range(3)]
    game_state.silver_fish = SilverFish(game_state.allsprites, game_state.images)
    game_state.snake = Snake(game_state.allsprites, game_state.images)
    game_state.seahorse = Seahorse(game_state.allsprites, game_state.images)
    game_state.jellyfishes = [
        Jellyfish(game_state.allsprites, game_state.images)
        for _ in range(len(Jellyfish.JELLYFISHES_SCORE_TO_SPAWN))
    ]
    game_state.sharks = []
    game_state.silver_arrow_warnings = []
    for _ in range(len(Shark.SHARKS_SCORES_TO_SPAWN)):
        shark = Shark(game_state.allsprites, game_state.images)
        game_state.sharks.append(shark)
        game_state.silver_arrow_warnings.append(
            ArrowWarning(game_state.arrow_warning_sprites, "silver", shark)
        )

    game_state.star = StarPowerup(game_state.allsprites, game_state.images)
    game_state.rainbow_fish = RainbowFish(game_state.allsprites, game_state.images)
    game_state.red_arrow_warning = ArrowWarning(
        game_state.arrow_warning_sprites, "red", game_state.rainbow_fish
    )
    game_state.bright_blue_fish = BrightBlueFish(game_state.allsprites, game_state.images)
    game_state.blue_arrow_warning_left = ArrowWarning(
        game_state.arrow_warning_sprites, "blue", game_state.bright_blue_fish, "left"
    )
    game_state.blue_arrow_warning_right = ArrowWarning(
        game_state.arrow_warning_sprites, "blue", game_state.bright_blue_fish, "right"
    )
