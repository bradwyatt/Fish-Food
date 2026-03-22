import random

import pygame

from utils import IMAGES


class Seaweed(pygame.sprite.Sprite):
    def __init__(self, allsprites, x_pos, y_pos):
        super().__init__()
        self.image = IMAGES["spr_seaweed"]
        self.rect = self.image.get_rect()
        self.rect.topleft = x_pos, y_pos
        self.seaweed_animate_timer = random.randint(0, 30)
        allsprites.add(self)

    def update(self):
        self.seaweed_animate_timer += 1
        seaweed_images = [
            IMAGES["spr_seaweed"],
            IMAGES["spr_seaweed_left"],
            IMAGES["spr_seaweed_right"],
        ]
        if 15 < self.seaweed_animate_timer < 30:
            self.image = seaweed_images[1]
        if self.seaweed_animate_timer >= 30:
            self.image = seaweed_images[2]
        if self.seaweed_animate_timer > 45:
            self.seaweed_animate_timer = 0
            self.image = seaweed_images[0]

    def remove_sprite(self):
        self.kill()
