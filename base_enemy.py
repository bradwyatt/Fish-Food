import pygame


class BaseEnemy(pygame.sprite.Sprite):
    def reset_position(self):
        self._prepare_for_reset()
        self.rect.topleft = self._random_spawn_position()
        self._finish_reset()

    def _prepare_for_reset(self):
        pass

    def _finish_reset(self):
        pass

    def _random_spawn_position(self):
        raise NotImplementedError

    def rebuild_alpha_surface(self, source_image=None):
        source_image = source_image or self.original_image
        self.alpha_surface = pygame.Surface(source_image.get_size(), pygame.SRCALPHA)
        self.alpha_surface.blit(source_image, (0, 0))
        self.alpha_surface.set_alpha(getattr(self, "alpha", 255))
        return self.alpha_surface

    def begin_fade_in(self, fade_rate=2, max_alpha=255, delay_ms=0):
        self.alpha = 0
        self.max_alpha = max_alpha
        self.fade_rate = fade_rate
        self.fading_in = delay_ms <= 0
        self.fade_in_start_time = pygame.time.get_ticks() + delay_ms if delay_ms > 0 else 0
        if hasattr(self, "visible"):
            self.visible = False
        if hasattr(self, "alpha_surface"):
            self.alpha_surface.set_alpha(self.alpha)

    def update_fade_in(self, current_time=None):
        current_time = pygame.time.get_ticks() if current_time is None else current_time

        if not getattr(self, "fading_in", False) and current_time >= getattr(self, "fade_in_start_time", 0):
            self.fading_in = True
            if hasattr(self, "visible"):
                self.visible = True

        if self.fading_in:
            if self.alpha < self.max_alpha:
                self.alpha = min(self.max_alpha, self.alpha + self.fade_rate)
                if hasattr(self, "alpha_surface"):
                    self.alpha_surface.set_alpha(self.alpha)
            else:
                self.fading_in = False
