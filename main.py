import asyncio

import pygame

from collisions import collide_mask_to_mask, collide_rect_to_mask
from game_app import GameApp
from game_state import GameState
from utils import SCREEN_HEIGHT, SCREEN_WIDTH, load_all_assets


async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fish Food")
    gameicon = pygame.image.load("sprites/red_fish_ico.png")
    pygame.display.set_icon(gameicon)
    clock = pygame.time.Clock()
    load_all_assets()
    app = GameApp(screen, clock)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
