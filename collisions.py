import pygame


def collide_rect_to_mask(sprite1, sprite2, mask_name="mask"):
    """
    Check for collision between sprite1's rect and a specified mask of sprite2.
    """
    if not pygame.sprite.collide_rect(sprite1, sprite2):
        return False

    mask1 = pygame.mask.Mask((sprite1.rect.width, sprite1.rect.height))
    mask1.fill()

    mask2 = getattr(sprite2, mask_name, None)
    if mask2 is None:
        raise ValueError(f"Mask '{mask_name}' not found in sprite2")

    offset_x = sprite2.rect.left - sprite1.rect.left
    offset_y = sprite2.rect.top - sprite1.rect.top
    return mask1.overlap(mask2, (offset_x, offset_y)) is not None


def collide_mask_to_mask(sprite1, mask1_name, sprite2, mask2_name, use_rect_check=True):
    """
    Check for collision between two masks with an optional rect pre-check.
    """
    mask1 = getattr(sprite1, mask1_name, None)
    mask2 = getattr(sprite2, mask2_name, None)

    if not mask1 or not mask2:
        return False

    if use_rect_check and not sprite1.rect.colliderect(sprite2.rect):
        return False

    offset_x = sprite2.rect.left - sprite1.rect.left
    offset_y = sprite2.rect.top - sprite1.rect.top
    return mask1.overlap(mask2, (offset_x, offset_y)) is not None
