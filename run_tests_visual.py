#!/usr/bin/env python3
"""
run_tests_visual.py  —  Pygame window showing Fish-Food headless test results.

Usage:
    python run_tests_visual.py
    python run_tests_visual.py -k movement   # filter by name substring
"""

import os
import sys
import subprocess
import time
import re

# ── Run the tests as a subprocess so their headless SDL setup
#    doesn't conflict with our display window. ────────────────────────────────
def _run_tests(keyword=None):
    """Run test_headless.py via stdlib unittest — no pytest needed."""
    here = os.path.dirname(os.path.abspath(__file__))
    proc = subprocess.run(
        [sys.executable, "test_headless.py"],
        capture_output=True, text=True, cwd=here,
    )
    return proc.stdout + proc.stderr, keyword


def _parse_results(raw, keyword=None):
    """Return list of (class_name, test_name, status, detail_lines).

    Handles unittest verbose output (verbosity=2):
        test_foo (__main__.TestBar.test_foo) ... ok
        test_foo (__main__.TestBar.test_foo) ... FAIL
        test_foo (__main__.TestBar.test_foo) ... ERROR
        test_foo (__main__.TestBar.test_foo) ... skipped 'reason'
    """
    STATUS_MAP = {"ok": "PASSED", "FAIL": "FAILED", "ERROR": "ERROR", "skipped": "SKIPPED"}
    records = []
    current_detail = []
    current_test = None

    for line in raw.splitlines():
        m = re.match(r"^(test_\w+)\s+\(.*?(Test\w+).*?\)\s+\.\.\.\s+(ok|FAIL|ERROR|skipped)", line)
        if m:
            if current_test:
                records.append((*current_test, current_detail))
            name = m.group(1)
            cls  = m.group(2)
            status = STATUS_MAP.get(m.group(3), m.group(3).upper())
            current_test = (cls, name, status)
            current_detail = []
        elif current_test and line.strip() and not line.startswith(("-", "=")):
            current_detail.append(line)

    if current_test:
        records.append((*current_test, current_detail))

    # optional keyword filter
    if keyword:
        kw = keyword.lower()
        records = [(c, n, s, d) for c, n, s, d in records
                   if kw in n.lower() or kw in c.lower()]

    return records


# ── Pygame display ────────────────────────────────────────────────────────────
def _show(records, keyword=None):
    import pygame

    # --- layout constants ---
    W, H         = 860, 680
    PAD          = 18
    ROW_H        = 26
    HEADER_H     = 60
    SECTION_H    = 32
    FOOTER_H     = 56

    # --- palette ---
    BG           = (15,  25,  45)
    CARD_BG      = (22,  38,  65)
    SECTION_BG   = (30,  50,  85)
    PASS_BG      = (22,  90,  40)
    FAIL_BG      = (110, 22,  22)
    ERR_BG       = (100, 70,   0)
    SKIP_BG      = (40,  60, 100)
    PASS_TXT     = (120, 230, 130)
    FAIL_TXT     = (255, 110, 110)
    ERR_TXT      = (255, 190,  60)
    SKIP_TXT     = (130, 180, 255)
    TITLE_TXT    = (200, 220, 255)
    SECTION_TXT  = (160, 200, 255)
    NAME_TXT     = (210, 225, 250)
    SUMMARY_PASS = (80,  210, 100)
    SUMMARY_FAIL = (230,  70,  70)
    SCROLL_BAR   = (60,  80, 120)
    SCROLL_THUMB = (100, 140, 200)

    STATUS_COLORS = {
        "PASSED":  (PASS_BG,  PASS_TXT,  "PASS"),
        "FAILED":  (FAIL_BG,  FAIL_TXT,  "FAIL"),
        "ERROR":   (ERR_BG,   ERR_TXT,   "ERR "),
        "SKIPPED": (SKIP_BG,  SKIP_TXT,  "SKIP"),
    }

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Fish-Food  —  Test Results")

    try:
        font_lg  = pygame.font.SysFont("menlo, consolas, monospace", 20, bold=True)
        font_md  = pygame.font.SysFont("menlo, consolas, monospace", 15, bold=True)
        font_sm  = pygame.font.SysFont("menlo, consolas, monospace", 13)
        font_hdr = pygame.font.SysFont("menlo, consolas, monospace", 22, bold=True)
    except Exception:
        font_lg  = pygame.font.Font(None, 22)
        font_md  = pygame.font.Font(None, 17)
        font_sm  = pygame.font.Font(None, 15)
        font_hdr = pygame.font.Font(None, 24)

    # --- group by class ---
    sections = {}
    for cls, name, status, detail in records:
        sections.setdefault(cls, []).append((name, status, detail))

    # --- build content surface (scrollable) ---
    n_rows = sum(1 + len(tests) for tests in sections.values())
    content_h = n_rows * ROW_H + len(sections) * (SECTION_H - ROW_H) + PAD * 2
    content = pygame.Surface((W - 12, max(content_h, H - HEADER_H - FOOTER_H)))
    content.fill(BG)

    y = PAD
    for cls_name, tests in sections.items():
        # section header
        pygame.draw.rect(content, SECTION_BG, (0, y, content.get_width(), SECTION_H), border_radius=6)
        lbl = font_md.render(cls_name, True, SECTION_TXT)
        content.blit(lbl, (PAD, y + (SECTION_H - lbl.get_height()) // 2))
        y += SECTION_H + 2

        for name, status, detail in tests:
            bg, tc, badge = STATUS_COLORS.get(status, (CARD_BG, NAME_TXT, status[:4]))
            pygame.draw.rect(content, CARD_BG, (4, y, content.get_width() - 8, ROW_H - 2), border_radius=4)

            # badge
            badge_surf = font_sm.render(f" {badge} ", True, tc, bg)
            content.blit(badge_surf, (PAD, y + (ROW_H - badge_surf.get_height()) // 2))

            # test name
            name_surf = font_sm.render(name, True, NAME_TXT)
            content.blit(name_surf, (PAD + 60, y + (ROW_H - name_surf.get_height()) // 2))

            y += ROW_H

        y += 6  # gap between sections

    # --- stats ---
    total  = len(records)
    passed = sum(1 for _, _, s, _ in records if s == "PASSED")
    failed = sum(1 for _, _, s, _ in records if s in ("FAILED", "ERROR"))

    # --- scroll state ---
    scroll_y    = 0
    view_h      = H - HEADER_H - FOOTER_H
    max_scroll  = max(0, content.get_height() - view_h)
    dragging    = False
    drag_offset = 0

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - ROW_H * 3)
                elif event.key == pygame.K_DOWN:
                    scroll_y = min(max_scroll, scroll_y + ROW_H * 3)
                elif event.key == pygame.K_PAGEUP:
                    scroll_y = max(0, scroll_y - view_h)
                elif event.key == pygame.K_PAGEDOWN:
                    scroll_y = min(max_scroll, scroll_y + view_h)
                elif event.key == pygame.K_HOME:
                    scroll_y = 0
                elif event.key == pygame.K_END:
                    scroll_y = max_scroll
            elif event.type == pygame.MOUSEWHEEL:
                scroll_y = max(0, min(max_scroll, scroll_y - event.y * ROW_H * 2))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                bar_x = W - 10
                if mx >= bar_x and max_scroll > 0:
                    dragging = True
                    drag_offset = my
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                dy = event.pos[1] - drag_offset
                drag_offset = event.pos[1]
                ratio = dy / view_h
                scroll_y = max(0, min(max_scroll, scroll_y + int(ratio * content.get_height())))

        # --- draw ---
        screen.fill(BG)

        # header
        pygame.draw.rect(screen, CARD_BG, (0, 0, W, HEADER_H))
        title = font_hdr.render("Fish-Food  —  Test Results", True, TITLE_TXT)
        screen.blit(title, (PAD, (HEADER_H - title.get_height()) // 2))

        sub_color = SUMMARY_PASS if failed == 0 else SUMMARY_FAIL
        sub_text  = f"{passed}/{total} passed" + (f"  ·  {failed} failed" if failed else "")
        sub = font_md.render(sub_text, True, sub_color)
        screen.blit(sub, (W - PAD - sub.get_width(), (HEADER_H - sub.get_height()) // 2))

        # scrollable content
        clip = pygame.Rect(0, HEADER_H, W - 12, view_h)
        screen.set_clip(clip)
        screen.blit(content, (0, HEADER_H - scroll_y))
        screen.set_clip(None)

        # scrollbar
        if max_scroll > 0:
            bar_h   = max(24, int(view_h * view_h / content.get_height()))
            bar_top = HEADER_H + int((view_h - bar_h) * scroll_y / max_scroll)
            pygame.draw.rect(screen, SCROLL_BAR,  (W - 10, HEADER_H, 8, view_h), border_radius=4)
            pygame.draw.rect(screen, SCROLL_THUMB, (W - 10, bar_top, 8, bar_h), border_radius=4)

        # footer
        pygame.draw.rect(screen, CARD_BG, (0, H - FOOTER_H, W, FOOTER_H))
        hint = font_sm.render("scroll: mouse wheel  ·  close: Q or Esc", True, (90, 110, 150))
        screen.blit(hint, (PAD, H - FOOTER_H + (FOOTER_H - hint.get_height()) // 2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    keyword = None
    args = sys.argv[1:]
    if "-k" in args:
        idx = args.index("-k")
        if idx + 1 < len(args):
            keyword = args[idx + 1]

    print("Running tests...", flush=True)
    raw, keyword = _run_tests(keyword)
    records = _parse_results(raw, keyword)

    if not records:
        print("Could not parse test output. Raw output:")
        print(raw)
        sys.exit(1)

    _show(records, keyword)
