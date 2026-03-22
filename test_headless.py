"""
test_headless.py - Headless regression tests for Fish-Food.

Covers the verification checklist in REFACTORING_PLAN.md:
  - Asset loading
  - GameState initialisation and entity counts
  - Score milestone activations (sharks, jellyfish, bright-blue fish, rainbow fish)
  - Player movement and boundary enforcement
  - Collision detection helpers (collide_rect_to_mask, collide_mask_to_mask)
  - High-score persistence (save, reload, tamper detection)
  - Game-over state transition

Run:
    python test_headless.py          # standard unittest runner
    python -m pytest test_headless.py -v
"""

import os
import sys
import asyncio
import shutil
import tempfile
import unittest

# ── Headless SDL setup — must precede any pygame import ──────────────────────
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Ensure relative asset paths (sprites/, sounds/, fonts/) resolve correctly.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Prevent the module-level asyncio.run(main()) in main.py from starting the
# game loop when we import it.
_real_asyncio_run = asyncio.run
def _suppress_asyncio_run(coro, **kw):
    coro.close()
    return None
asyncio.run = _suppress_asyncio_run

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((1024, 600))  # dummy surface; needed for image loading

import main as _game  # noqa: E402  (asyncio.run is patched above)
from main import GameState, collide_rect_to_mask, collide_mask_to_mask  # noqa: E402
from utils import IMAGES, SOUNDS, FONTS, SCREEN_WIDTH, SCREEN_HEIGHT  # noqa: E402
from high_score import HighScoreStore  # noqa: E402
import shark as _shark_mod  # noqa: E402
import jellyfish as _jf_mod  # noqa: E402
import rainbow_fish as _rf_mod  # noqa: E402
import bright_blue_fish as _bbf_mod  # noqa: E402

asyncio.run = _real_asyncio_run  # restore for anything that may need it later

# ── Load assets once for the whole test session ───────────────────────────────
try:
    _game.load_all_assets()
except Exception as _exc:
    print(f"[warn] load_all_assets partial failure (expected in headless): {_exc}")


# ── Shared helpers ────────────────────────────────────────────────────────────

def _make_gs():
    """Return a fresh GameState with an in-memory (disabled) high-score store."""
    return GameState(IMAGES, high_score_store=HighScoreStore(enabled=False))


def _surf():
    """Minimal surface to pass as 'zoomed_surface' to update/activate methods."""
    return pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


class _MockSprite(pygame.sprite.Sprite):
    """Opaque filled-rect sprite with mask — used for collision helper tests."""
    def __init__(self, x=100, y=100, w=32, h=32):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.face_mask = self.mask
        self.body_mask = self.mask


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Asset loading
# ═══════════════════════════════════════════════════════════════════════════════
class TestAssetLoading(unittest.TestCase):
    EXPECTED_IMAGE_KEYS = [
        "player_right",
        "spr_red_fish",
        "spr_green_fish_right",
        "spr_shark_right",
        "spr_silver_fish",
        "spr_rainbow_fish_right",
        "spr_jellyfish_1",
        "spr_seahorse",
        "spr_snake_1",
        "spr_star_1",
        "spr_bright_blue_fish_right",
    ]

    def test_images_populated(self):
        self.assertGreater(len(IMAGES), 0)

    def test_expected_image_keys_present(self):
        for key in self.EXPECTED_IMAGE_KEYS:
            with self.subTest(key=key):
                self.assertIn(key, IMAGES)

    def test_fonts_populated(self):
        self.assertGreater(len(FONTS), 0)

    def test_sounds_populated(self):
        self.assertGreater(len(SOUNDS), 0)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. GameState initialisation
# ═══════════════════════════════════════════════════════════════════════════════
class TestGameStateInit(unittest.TestCase):
    def setUp(self):
        self.gs = _make_gs()

    def test_initial_score_is_zero(self):
        self.assertEqual(self.gs.score, 0)

    def test_initial_state_is_start_screen(self):
        self.assertEqual(self.gs.current_state, GameState.START_SCREEN)

    def test_red_fish_count(self):
        self.assertEqual(len(self.gs.red_fishes), 6)

    def test_green_fish_count(self):
        self.assertEqual(len(self.gs.green_fishes), 3)

    def test_shark_count_matches_threshold_list(self):
        self.assertEqual(len(self.gs.sharks), len(_shark_mod.Shark.SHARKS_SCORES_TO_SPAWN))

    def test_jellyfish_count_matches_threshold_list(self):
        self.assertEqual(len(self.gs.jellyfishes), len(_jf_mod.Jellyfish.JELLYFISHES_SCORE_TO_SPAWN))

    def test_walls_created(self):
        self.assertGreater(len(self.gs.walls), 0)

    def test_player_exists(self):
        self.assertIsNotNone(self.gs.player)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Shark spawn thresholds  [5, 20, 45, 75]
# ═══════════════════════════════════════════════════════════════════════════════
class TestSharkThresholds(unittest.TestCase):
    THRESHOLDS = _shark_mod.Shark.SHARKS_SCORES_TO_SPAWN

    def setUp(self):
        self.gs = _make_gs()

    def test_shark_not_activated_below_threshold(self):
        self.gs.score = self.THRESHOLDS[0] - 1
        self.gs.activate_game_objects(_surf())
        self.assertFalse(self.gs.sharks[0].activate)

    def test_all_sharks_activate_at_their_threshold(self):
        for idx, threshold in enumerate(self.THRESHOLDS):
            with self.subTest(shark_index=idx, threshold=threshold):
                self.gs.score = threshold
                self.gs.activate_game_objects(_surf())
                self.assertTrue(
                    self.gs.sharks[idx].activate,
                    f"shark[{idx}] should be active at score {threshold}",
                )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Jellyfish spawn thresholds  [0, 30, 60]
# ═══════════════════════════════════════════════════════════════════════════════
class TestJellyfishThresholds(unittest.TestCase):
    THRESHOLDS = _jf_mod.Jellyfish.JELLYFISHES_SCORE_TO_SPAWN

    def setUp(self):
        self.gs = _make_gs()

    def test_all_jellyfishes_activate_at_their_threshold(self):
        for idx, threshold in enumerate(self.THRESHOLDS):
            with self.subTest(jf_index=idx, threshold=threshold):
                self.gs.score = threshold
                self.gs.activate_game_objects(_surf())
                self.assertTrue(
                    self.gs.jellyfishes[idx].activate,
                    f"jellyfishes[{idx}] should be active at score {threshold}",
                )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Rainbow fish timer threshold  (1200 ticks)
# ═══════════════════════════════════════════════════════════════════════════════
class TestRainbowFishTimer(unittest.TestCase):
    TICKS = _rf_mod.RainbowFish.NUM_OF_TICKS_FOR_ENTRANCE

    def setUp(self):
        self.gs = _make_gs()

    def test_not_active_before_timer(self):
        self.gs.rainbow_fish.rainbow_timer = self.TICKS - 1
        self.gs.activate_game_objects(_surf())
        self.assertFalse(self.gs.rainbow_fish.is_active)

    def test_active_at_timer_threshold(self):
        self.gs.rainbow_fish.rainbow_timer = self.TICKS
        self.gs.activate_game_objects(_surf())
        self.assertTrue(self.gs.rainbow_fish.is_active)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Bright blue fish threshold  (score 50+)
# ═══════════════════════════════════════════════════════════════════════════════
class TestBrightBlueFishThreshold(unittest.TestCase):
    SCORE = _bbf_mod.BrightBlueFish.ACTIVATION_SCORE  # 50

    def setUp(self):
        self.gs = _make_gs()

    def test_not_activated_below_threshold(self):
        activated = self.gs.bright_blue_fish.try_activate(self.SCORE - 1, 0)
        self.assertFalse(activated)
        self.assertFalse(self.gs.bright_blue_fish.activate)

    def test_activates_at_threshold_when_offscreen(self):
        # Fish starts offscreen by default; is_out_of_world() must return True.
        activated = self.gs.bright_blue_fish.try_activate(self.SCORE, 0)
        self.assertTrue(activated)
        self.assertTrue(self.gs.bright_blue_fish.activate)

    def test_does_not_reactivate_at_same_score_bracket(self):
        # Already activated at score=50; same bracket should not fire again.
        self.gs.bright_blue_fish.try_activate(self.SCORE, 0)
        activated_again = self.gs.bright_blue_fish.try_activate(self.SCORE, self.SCORE)
        self.assertFalse(activated_again)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Collision detection helpers
# ═══════════════════════════════════════════════════════════════════════════════
class TestCollisionHelpers(unittest.TestCase):
    def test_rect_to_mask_detects_overlap(self):
        s1, s2 = _MockSprite(100, 100), _MockSprite(100, 100)
        self.assertTrue(collide_rect_to_mask(s1, s2))

    def test_rect_to_mask_no_overlap_far_apart(self):
        s1, s2 = _MockSprite(0, 0), _MockSprite(500, 500)
        self.assertFalse(collide_rect_to_mask(s1, s2))

    def test_mask_to_mask_detects_overlap(self):
        s1, s2 = _MockSprite(100, 100), _MockSprite(100, 100)
        self.assertTrue(collide_mask_to_mask(s1, "mask", s2, "mask"))

    def test_mask_to_mask_no_overlap_far_apart(self):
        s1, s2 = _MockSprite(0, 0), _MockSprite(500, 500)
        self.assertFalse(collide_mask_to_mask(s1, "mask", s2, "mask"))

    def test_partial_pixel_overlap_detected(self):
        s1 = _MockSprite(100, 100, 32, 32)
        s2 = _MockSprite(116, 116, 32, 32)  # 16 px overlap in both axes
        self.assertTrue(collide_rect_to_mask(s1, s2))

    def test_adjacent_sprites_do_not_collide(self):
        s1 = _MockSprite(100, 100, 32, 32)
        s2 = _MockSprite(132, 100, 32, 32)  # touching edge only — zero pixel overlap
        self.assertFalse(collide_rect_to_mask(s1, s2))

    def test_face_mask_attribute_used(self):
        s1 = _MockSprite(100, 100)
        s2 = _MockSprite(100, 100)
        # face_mask is set on _MockSprite; collision via named mask should work
        self.assertTrue(collide_rect_to_mask(s1, s2, "face_mask"))

    def test_body_mask_attribute_used(self):
        s1 = _MockSprite(100, 100)
        s2 = _MockSprite(100, 100)
        self.assertTrue(collide_mask_to_mask(s1, "body_mask", s2, "body_mask"))


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Player eating a red fish increases score
# ═══════════════════════════════════════════════════════════════════════════════
class TestPlayerEatsRedFish(unittest.TestCase):
    def setUp(self):
        self.gs = _make_gs()
        self.gs.current_state = GameState.PLAY_SCREEN
        # One update pass so all sprites have image/mask attributes set.
        self.gs.allsprites.update()

    def test_score_increases_on_red_fish_collision(self):
        player = self.gs.player
        red_fish = self.gs.red_fishes[0]
        # Make fish visible and place it directly over the player.
        red_fish.image.set_alpha(255)
        red_fish.rect.topleft = player.rect.topleft
        before = self.gs.score
        self.gs.handle_collisions()
        self.assertGreater(self.gs.score, before)

    def test_score_increases_by_correct_amount(self):
        player = self.gs.player
        red_fish = self.gs.red_fishes[0]
        red_fish.image.set_alpha(255)
        red_fish.rect.topleft = player.rect.topleft
        expected = red_fish.get_score_value()
        before = self.gs.score
        self.gs.handle_collisions()
        self.assertEqual(self.gs.score - before, expected)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Player movement and boundary enforcement
# ═══════════════════════════════════════════════════════════════════════════════
class TestPlayerMovement(unittest.TestCase):
    """Movement updates self.pos; rect syncs in update(). Test pos directly."""

    def setUp(self):
        self.gs = _make_gs()
        self.p = self.gs.player

    def test_move_right_increases_pos_x(self):
        x0 = self.p.pos[0]
        self.p.move_right()
        self.assertGreater(self.p.pos[0], x0)

    def test_move_left_decreases_pos_x(self):
        for _ in range(20):          # move away from left edge first
            self.p.move_right()
        x0 = self.p.pos[0]
        self.p.move_left()
        self.assertLess(self.p.pos[0], x0)

    def test_move_up_decreases_pos_y(self):
        for _ in range(20):
            self.p.move_down()
        y0 = self.p.pos[1]
        self.p.move_up()
        self.assertLess(self.p.pos[1], y0)

    def test_move_down_increases_pos_y(self):
        y0 = self.p.pos[1]
        self.p.move_down()
        self.assertGreater(self.p.pos[1], y0)

    def test_pos_clamped_at_left_boundary(self):
        # Guard is "if pos > 32: move", so final pos is in [32-speed, 32].
        for _ in range(500):
            self.p.move_left()
        self.assertGreaterEqual(self.p.pos[0], 32 - self.p.speed_x)

    def test_pos_clamped_at_right_boundary(self):
        # Guard is "if pos < WIDTH-75: move", so final pos is in [WIDTH-75, WIDTH-75+speed].
        for _ in range(500):
            self.p.move_right()
        self.assertLessEqual(self.p.pos[0], SCREEN_WIDTH - 75 + self.p.speed_x)

    def test_pos_clamped_at_top_boundary(self):
        # Guard is "if pos > 50: move", so final pos is in [50-speed, 50].
        for _ in range(500):
            self.p.move_up()
        self.assertGreaterEqual(self.p.pos[1], 50 - self.p.speed_y)

    def test_pos_clamped_at_bottom_boundary(self):
        # Guard is "if pos < HEIGHT-75: move", so final pos is in [HEIGHT-75, HEIGHT-75+speed].
        for _ in range(500):
            self.p.move_down()
        self.assertLessEqual(self.p.pos[1], SCREEN_HEIGHT - 75 + self.p.speed_y)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. High-score persistence
# ═══════════════════════════════════════════════════════════════════════════════
class TestHighScorePersistence(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _store(self):
        return HighScoreStore(enabled=True, base_path=self._tmp)

    def test_load_nonexistent_returns_zero(self):
        self.assertEqual(self._store().load(), 0)

    def test_save_and_reload(self):
        self._store().save(9999)
        self.assertEqual(self._store().load(), 9999)

    def test_second_save_overwrites_first(self):
        self._store().save(100)
        self._store().save(200)
        self.assertEqual(self._store().load(), 200)

    def test_disabled_store_always_returns_zero(self):
        store = HighScoreStore(enabled=False, base_path=self._tmp)
        store.save(5000)
        self.assertEqual(store.load(), 0)

    def test_negative_score_clamped_to_zero(self):
        self._store().save(-50)
        self.assertEqual(self._store().load(), 0)

    def test_tampered_file_returns_zero(self):
        self._store().save(100)
        save_path = os.path.join(self._tmp, ".fishfood_save.dat")
        with open(save_path, "w") as f:
            f.write('{"payload":"baddata","signature":"badsig"}')
        self.assertEqual(self._store().load(), 0)

    def test_finalize_high_score_saves_when_beaten(self):
        store = HighScoreStore(enabled=True, base_path=self._tmp)
        gs = GameState(IMAGES, high_score_store=store)
        gs.score = 99
        gs.finalize_high_score()
        self.assertEqual(store.load(), 99)

    def test_finalize_high_score_does_not_save_lower_score(self):
        store = HighScoreStore(enabled=True, base_path=self._tmp)
        store.save(500)
        gs = GameState(IMAGES, high_score_store=store)
        gs.score = 10
        gs.finalize_high_score()
        self.assertEqual(store.load(), 500)


# ═══════════════════════════════════════════════════════════════════════════════
# 11. Game-over state transition
# ═══════════════════════════════════════════════════════════════════════════════
class TestGameOverTransition(unittest.TestCase):
    def setUp(self):
        self.gs = _make_gs()
        self.gs.current_state = GameState.PLAY_SCREEN

    def test_transitions_to_game_over_screen_after_timer(self):
        self.gs.player.game_over = True
        limit = GameState.TIMER_UNTIL_GAME_OVER_SCREEN
        for _ in range(limit + 5):
            self.gs.update(_surf())
        self.assertEqual(self.gs.current_state, GameState.GAME_OVER_SCREEN)

    def test_no_transition_when_player_alive(self):
        self.gs.player.game_over = False
        # Init sprites so handle_collisions() can access image/mask attributes.
        self.gs.allsprites.update()
        for _ in range(200):
            self.gs.update(_surf())
        self.assertNotEqual(self.gs.current_state, GameState.GAME_OVER_SCREEN)

    def test_game_over_processed_flag_set(self):
        self.gs.player.game_over = True
        limit = GameState.TIMER_UNTIL_GAME_OVER_SCREEN
        for _ in range(limit + 5):
            self.gs.update(_surf())
        self.assertTrue(self.gs.game_over_processed)

    def test_high_score_saved_on_game_over(self):
        tmp = tempfile.mkdtemp()
        store = HighScoreStore(enabled=True, base_path=tmp)
        gs = GameState(IMAGES, high_score_store=store)
        gs.current_state = GameState.PLAY_SCREEN
        gs.score = 42
        gs.player.game_over = True
        limit = GameState.TIMER_UNTIL_GAME_OVER_SCREEN
        for _ in range(limit + 5):
            gs.update(_surf())
        self.assertEqual(store.load(), 42)
        shutil.rmtree(tmp, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Powerup collection smoke tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestPowerupCollection(unittest.TestCase):
    """Verify powerup collisions run without errors and apply their effects."""

    def setUp(self):
        self.gs = _make_gs()
        self.gs.current_state = GameState.PLAY_SCREEN
        # Init sprites so handle_collisions() can access image/mask attributes.
        self.gs.allsprites.update()

    def test_seahorse_collection_does_not_crash(self):
        seahorse = self.gs.seahorse
        seahorse.rect.topleft = self.gs.player.rect.topleft
        try:
            self.gs.handle_collisions()
        except Exception as exc:
            self.fail(f"Seahorse collision raised: {exc}")

    def test_star_collection_does_not_crash(self):
        # Star uses rect collision (no mask needed)
        self.gs.star.rect.topleft = self.gs.player.rect.topleft
        try:
            self.gs.handle_collisions()
        except Exception as exc:
            self.fail(f"Star collision raised: {exc}")

    def test_star_activates_player_powerup(self):
        from player import Player
        self.gs.star.rect.topleft = self.gs.player.rect.topleft
        self.gs.handle_collisions()
        self.assertIn(
            self.gs.player.star_power,
            (Player.INVINCIBLE_POWERUP, Player.SHARK_SHRINKER_POWERUP),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
