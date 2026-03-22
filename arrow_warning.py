import pygame

from utils import IMAGES, SCREEN_WIDTH


class ArrowWarning(pygame.sprite.Sprite):
    def __init__(self, arrow_warning_sprites, arrow_type, target_sprite, side="top"):
        super().__init__()
        self.arrow_type = arrow_type
        self.image = IMAGES[f"arrow_warning_{arrow_type}_{side}"]
        self.rect = self.image.get_rect()
        self.target_sprite = target_sprite
        self.side = side

        if side == "top":
            self.rect.y = 40
            self.rect.x = self.target_sprite.rect.left
        elif side == "left":
            self.rect.x = SCREEN_WIDTH - 100
            self.rect.y = self.target_sprite.rect.centery
        elif side == "right":
            self.rect.x = 50
            self.rect.y = self.target_sprite.rect.centery

        arrow_warning_sprites.add(self)
        self.visible = False

    def update(self):
        if self.side == "top":
            self.rect.x = self.target_sprite.rect.left
        elif self.side in {"left", "right"}:
            self.rect.y = self.target_sprite.rect.centery
