import pygame


class Wall(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        allsprites.add(self)

    def remove_sprite(self):
        self.kill()
