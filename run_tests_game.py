#!/usr/bin/env python3
"""
run_tests_game.py  —  Visual test scenarios inside the actual Fish-Food game.

Each test sets up a situation, lets it play out on screen, then shows PASS/FAIL.
Press SPACE to skip ahead, Q to quit.

Usage:
    python run_tests_game.py
"""

import os
import sys
import asyncio

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Patch asyncio.run BEFORE importing main.py so the game loop doesn't start.
_real_asyncio_run = asyncio.run
def _suppress_asyncio_run(coro, **kw):
    coro.close()
    return None
asyncio.run = _suppress_asyncio_run

import pygame
pygame.init()

from utils import SCREEN_WIDTH, SCREEN_HEIGHT, IMAGES, SOUNDS, FONTS

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fish-Food — Visual Test Scenarios")
clock = pygame.time.Clock()
FPS = 60

import main as _game
from main import GameState
from high_score import HighScoreStore
from player import Player
import shark as _shark_mod
import jellyfish as _jf_mod
import rainbow_fish as _rf_mod
import bright_blue_fish as _bbf_mod

asyncio.run = _real_asyncio_run

try:
    _game.load_all_assets()
except Exception as e:
    print(f"[warn] asset load partial: {e}")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _gs():
    return GameState(IMAGES, high_score_store=HighScoreStore(enabled=False))

def _surf():
    return pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

def _font(key, fallback_size=22):
    return FONTS.get(key) or pygame.font.Font(None, fallback_size)

def _events():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            return "quit"
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_q:      return "quit"
            if e.key == pygame.K_SPACE:  return "skip"
    return None

def _render_game(gs):
    bg = IMAGES.get("play_background")
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill((20, 40, 80))
    ground = IMAGES.get("ground")
    if ground:
        screen.blit(ground, (0, SCREEN_HEIGHT - 100))
    for sprite in gs.allsprites:
        screen.blit(sprite.image, sprite.rect)

def _overlay(title, subtitle="", status=None):
    bar = pygame.Surface((SCREEN_WIDTH, 76), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 170))
    screen.blit(bar, (0, 0))

    f_title = _font("ocean_font_22", 26)
    f_sub   = _font("ocean_font_16", 18)

    screen.blit(f_title.render(title,    True, (220, 235, 255)), (18, 10))
    if subtitle:
        screen.blit(f_sub.render(subtitle, True, (150, 175, 210)), (18, 44))

    if status is not None:
        color = (60, 210, 80) if status else (210, 60, 60)
        label = f_title.render("PASS" if status else "FAIL", True, color)
        screen.blit(label, (SCREEN_WIDTH - label.get_width() - 18, 24))

    hint = f_sub.render("SPACE = skip  ·  Q = quit", True, (90, 110, 150))
    screen.blit(hint, (SCREEN_WIDTH - hint.get_width() - 10, SCREEN_HEIGHT - 22))

def _box(rect, color=(255, 220, 50), width=3):
    """Draw a highlight rectangle around a sprite."""
    pygame.draw.rect(screen, color, rect, width, border_radius=3)


# ── Generic scenario runner ───────────────────────────────────────────────────

def run_scenario(title, subtitle, setup, tick, check,
                 run_frames=180, hold_frames=120):
    """
    setup(gs)           — called once after the first allsprites.update()
    tick(gs, frame)     — called every frame during run_frames; draw highlights here
    check(gs) -> bool   — evaluated at end of run_frames (or when skip pressed)

    allsprites.update() is called EVERY frame so sprites always animate.
    """
    gs = _make_scenario_gs()
    setup(gs)

    result = None

    for frame in range(run_frames + hold_frames):
        action = _events()
        if action == "quit":
            return None

        # Always animate sprites so sharks descend, fish move, player fades, etc.
        gs.allsprites.update()

        # Evaluate result once (at end of run phase, or on skip)
        if result is None and (frame >= run_frames or action == "skip"):
            result = check(gs)

        _render_game(gs)
        tick(gs, frame)          # draw per-frame highlights on top of render
        _overlay(title, subtitle, result)
        pygame.display.flip()
        clock.tick(FPS)

    return result


def _make_scenario_gs():
    gs = _gs()
    gs.current_state = GameState.PLAY_SCREEN
    gs.allsprites.update()   # initialise all images / masks
    return gs


# ── Scenarios ─────────────────────────────────────────────────────────────────

def scenario_player_eats_red_fish():
    def setup(gs):
        gs.score = 0
        gs.red_fishes[0].image.set_alpha(255)
        gs.red_fishes[0].rect.center = (
            gs.player.rect.centerx + 180,
            gs.player.rect.centery,
        )

    def tick(gs, frame):
        src    = gs.red_fishes[0]
        target = gs.player
        if gs.score == 0:
            # Slide the red fish toward the player.
            dx = target.rect.centerx - src.rect.centerx
            dy = target.rect.centery - src.rect.centery
            src.rect.x += int(dx * 0.1)
            src.rect.y += int(dy * 0.1)
            src.image.set_alpha(255)
            gs.handle_collisions()
        _box(src.rect,    (255, 220, 50))
        _box(target.rect, (100, 200, 255))
        # Show score
        f = _font("ocean_font_22", 26)
        screen.blit(f.render(f"Score: {gs.score}", True, (255, 255, 255)),
                    (SCREEN_WIDTH - 160, 84))

    def check(gs): return gs.score > 0

    return run_scenario(
        "Player Eats Red Fish",
        "Red fish slides into player  →  score should increase",
        setup, tick, check, run_frames=120,
    )


def scenario_shark_threshold():
    threshold = _shark_mod.Shark.SHARKS_SCORES_TO_SPAWN[0]   # 5

    def setup(gs):
        gs.score = threshold - 1
        # Move the first shark just above the visible area so it descends on screen.
        gs.sharks[0].rect.topleft = (SCREEN_WIDTH // 2 - 57, -60)

    def tick(gs, frame):
        if frame == 30:
            gs.score = threshold
            gs.activate_game_objects(_surf())
        # Keep ticking so shark descends after activation.
        if gs.sharks[0].activate:
            gs.sharks[0].update()   # explicit update so descent is visible
        _box(gs.sharks[0].rect, (255, 80, 80))
        f = _font("ocean_font_16", 18)
        screen.blit(f.render(f"Score: {gs.score}  |  shark.activate = {gs.sharks[0].activate}",
                              True, (220, 220, 100)), (18, 84))

    def check(gs): return gs.sharks[0].activate

    return run_scenario(
        f"Shark Activates at Score {threshold}",
        f"Score increments to {threshold}  →  shark descends from above",
        setup, tick, check, run_frames=180,
    )


def scenario_jellyfish_threshold():
    threshold = _jf_mod.Jellyfish.JELLYFISHES_SCORE_TO_SPAWN[1]   # 30

    def setup(gs):
        gs.score = threshold - 1
        # Move jellyfish[1] near the center so it's visible.
        gs.jellyfishes[1].rect.center = (SCREEN_WIDTH // 2, 100)

    def tick(gs, frame):
        if frame == 30:
            gs.score = threshold
            gs.activate_game_objects(_surf())
        if gs.jellyfishes[1].activate:
            gs.jellyfishes[1].update()
        _box(gs.jellyfishes[1].rect, (180, 100, 255))
        f = _font("ocean_font_16", 18)
        screen.blit(f.render(f"Score: {gs.score}  |  jellyfish.activate = {gs.jellyfishes[1].activate}",
                              True, (220, 220, 100)), (18, 84))

    def check(gs): return gs.jellyfishes[1].activate

    return run_scenario(
        f"Jellyfish Activates at Score {threshold}",
        f"Score reaches {threshold}  →  second jellyfish activates",
        setup, tick, check, run_frames=180,
    )


def scenario_rainbow_fish_timer():
    ticks_needed = _rf_mod.RainbowFish.NUM_OF_TICKS_FOR_ENTRANCE   # 1200

    def setup(gs):
        gs.rainbow_fish.rainbow_timer = ticks_needed - 20
        # Move to visible area.
        gs.rainbow_fish.rect.center = (SCREEN_WIDTH // 2, 200)

    def tick(gs, frame):
        gs.rainbow_fish.rainbow_timer += 4   # fast-forward
        gs.activate_game_objects(_surf())
        if gs.rainbow_fish.is_active:
            gs.rainbow_fish.update()
        _box(gs.rainbow_fish.rect, (255, 100, 200))
        f = _font("ocean_font_16", 18)
        screen.blit(f.render(
            f"timer: {gs.rainbow_fish.rainbow_timer}  |  is_active = {gs.rainbow_fish.is_active}",
            True, (220, 220, 100)), (18, 84))

    def check(gs): return gs.rainbow_fish.is_active

    return run_scenario(
        "Rainbow Fish Timer",
        f"Timer fast-forwards past {ticks_needed}  →  rainbow fish activates",
        setup, tick, check, run_frames=150,
    )


def scenario_bright_blue_fish():
    score = _bbf_mod.BrightBlueFish.ACTIVATION_SCORE   # 50

    def setup(gs):
        gs.score = 0

    def tick(gs, frame):
        if frame == 30:
            gs.bright_blue_fish.try_activate(score, 0)
            gs.last_bbf_activation_score = score
        if gs.bright_blue_fish.activate:
            gs.bright_blue_fish.update()
        _box(gs.bright_blue_fish.rect, (100, 180, 255))
        f = _font("ocean_font_16", 18)
        screen.blit(f.render(f"activate = {gs.bright_blue_fish.activate}",
                              True, (220, 220, 100)), (18, 84))

    def check(gs): return gs.bright_blue_fish.activate

    return run_scenario(
        "Bright Blue Fish at Score 50",
        "try_activate(50)  →  fish sweeps across screen",
        setup, tick, check, run_frames=200,
    )


def scenario_player_boundary():
    def setup(gs):
        pass

    def tick(gs, frame):
        for _ in range(8):
            gs.player.move_left()
        gs.player.update()
        _box(gs.player.rect, (100, 220, 100))
        f = _font("ocean_font_16", 18)
        screen.blit(f.render(f"player.pos[0] = {gs.player.pos[0]:.1f}  (boundary = 32)",
                              True, (220, 220, 100)), (18, 84))

    def check(gs):
        return gs.player.pos[0] >= 32 - Player.REGULAR_MOVE_SPEED

    return run_scenario(
        "Player Left Boundary",
        "Player held against left wall  —  pos should stay near boundary",
        setup, tick, check, run_frames=120,
    )


def scenario_game_over():
    def setup(gs):
        gs.score = 42

    def tick(gs, frame):
        if frame == 20:
            gs.player.game_over = True
        gs.update(_surf())   # gs.update also calls allsprites indirectly
        _box(gs.player.rect, (220, 60, 60))
        f = _font("ocean_font_16", 18)
        screen.blit(f.render(
            f"game_over_timer: {gs.game_over_timer}  |  state: {gs.current_state}",
            True, (220, 220, 100)), (18, 84))

    def check(gs): return gs.current_state == GameState.GAME_OVER_SCREEN

    return run_scenario(
        "Game Over Transition",
        "Player death  →  player fades out  →  state = GAME_OVER_SCREEN",
        setup, tick, check, run_frames=220,
    )


def scenario_seahorse_powerup():
    def setup(gs):
        gs.seahorse.rect.center = (
            gs.player.rect.centerx,
            gs.player.rect.centery - 80,
        )

    def tick(gs, frame):
        if gs.player.speed_power != Player.SPEED_SURGE:
            if gs.player.pos[1] > gs.seahorse.rect.centery + 10:
                gs.player.move_up()
            gs.player.update()
            gs.handle_collisions()
        _box(gs.seahorse.rect, (255, 200, 50))
        _box(gs.player.rect,   (100, 220, 100))
        f = _font("ocean_font_16", 18)
        screen.blit(f.render(f"speed_power = {gs.player.speed_power}  (SPEED_SURGE = {Player.SPEED_SURGE})",
                              True, (220, 220, 100)), (18, 84))

    def check(gs): return gs.player.speed_power == Player.SPEED_SURGE

    return run_scenario(
        "Seahorse Speed Powerup",
        "Player moves into seahorse  →  speed_power = SPEED_SURGE",
        setup, tick, check, run_frames=150,
    )


def scenario_high_score():
    import tempfile, shutil
    tmpdir = tempfile.mkdtemp()
    store  = HighScoreStore(enabled=True, base_path=tmpdir)
    store.save(999)
    loaded = store.load()
    passed = (loaded == 999)
    shutil.rmtree(tmpdir, ignore_errors=True)

    gs = _make_scenario_gs()
    f_md = _font("ocean_font_22", 26)
    f_sm = _font("ocean_font_16", 18)

    for frame in range(180):
        action = _events()
        if action in ("quit", "skip"):
            return None if action == "quit" else passed
        gs.allsprites.update()
        _render_game(gs)
        _overlay("High-Score Persistence",
                 "save(999) → load() should return 999", passed)
        line1 = f_md.render("Saved: 999", True, (200, 220, 255))
        line2 = f_md.render(f"Loaded: {loaded}", True,
                             (70, 215, 90) if passed else (215, 65, 65))
        cx = SCREEN_WIDTH // 2
        screen.blit(line1, (cx - line1.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(line2, (cx - line2.get_width() // 2, SCREEN_HEIGHT // 2 + 16))
        pygame.display.flip()
        clock.tick(FPS)

    return passed


# ── Summary screen ────────────────────────────────────────────────────────────

def show_summary(results):
    f_lg = _font("ocean_font_48", 52)
    f_md = _font("ocean_font_22", 26)
    f_sm = _font("ocean_font_16", 18)
    bg   = IMAGES.get("play_background")

    while True:
        if _events() in ("quit", "skip"):
            return

        if bg:  screen.blit(bg, (0, 0))
        else:   screen.fill((10, 20, 50))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        title = f_lg.render("Test Results", True, (200, 220, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 36))

        passed = sum(1 for _, r in results if r)
        y = 130
        for name, result in results:
            color = (70, 215, 90) if result else (215, 65, 65)
            badge = f_sm.render(f"[{'PASS' if result else 'FAIL'}]", True, color)
            label = f_sm.render(name, True, (210, 225, 250))
            screen.blit(badge, (SCREEN_WIDTH // 2 - 240, y))
            screen.blit(label, (SCREEN_WIDTH // 2 - 165, y))
            y += 30

        total = len(results)
        s_color = (70, 215, 90) if passed == total else (215, 65, 65)
        summary = f_md.render(f"{passed} / {total} passed", True, s_color)
        screen.blit(summary, (SCREEN_WIDTH // 2 - summary.get_width() // 2, y + 24))

        hint = f_sm.render("Press any key to exit", True, (90, 110, 150))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 32))

        pygame.display.flip()
        clock.tick(FPS)


# ── Main ──────────────────────────────────────────────────────────────────────

SCENARIOS = [
    ("Player Eats Red Fish",        scenario_player_eats_red_fish),
    ("Shark Activates at Score 5",  scenario_shark_threshold),
    ("Jellyfish at Score 30",       scenario_jellyfish_threshold),
    ("Rainbow Fish Timer",          scenario_rainbow_fish_timer),
    ("Bright Blue Fish at 50",      scenario_bright_blue_fish),
    ("Player Boundary",             scenario_player_boundary),
    ("Game Over Transition",        scenario_game_over),
    ("Seahorse Powerup",            scenario_seahorse_powerup),
    ("High-Score Persistence",      scenario_high_score),
]

if __name__ == "__main__":
    results = []
    for name, fn in SCENARIOS:
        r = fn()
        if r is None:
            break
        results.append((name, r))

    if results:
        show_summary(results)

    pygame.quit()
