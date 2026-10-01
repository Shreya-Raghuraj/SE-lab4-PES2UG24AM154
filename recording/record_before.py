"""
Records Lab-4/videos/before.mp4: 10 s of the UNMODIFIED starter game.

Clicks are aimed at specific spots on real targets to expose the
hit-detection bug: the hitbox is a square whose top-left corner sits at
the circle's centre, so
  * a click just inside the upper-left edge of a target  -> MISS (wrong)
  * a click clearly outside the lower-right edge          -> HIT  (wrong)
The dashed yellow square is a debug overlay of that buggy hitbox.
"""

import os
import random

from recorder import FPS, VideoWriter, draw_caption, draw_cursor, lerp, pygame

from game.game_engine import GameEngine
from game.renderer import WINDOW_SIZE

OUT = os.path.join(os.path.dirname(__file__), "..", "videos", "before.mp4")
DURATION = 10.0

# (kind, offset factor in radii from target centre, expected result)
SHOTS = [
    ("centre", (0.0, 0.0), "HIT"),
    ("inside upper-left edge", (-0.6, -0.6), "HIT"),
    ("outside lower-right edge", (1.5, 1.5), "MISS"),
    ("inside left edge", (-0.8, 0.0), "HIT"),
    ("outside lower-right edge", (1.7, 1.2), "MISS"),
    ("inside top edge", (0.0, -0.85), "HIT"),
    ("outside lower-right edge", (1.2, 1.7), "MISS"),
]


def dashed_rect(surface, rect, color):
    x0, y0, x1, y1 = rect.left, rect.top, rect.right, rect.bottom
    for x in range(x0, x1, 8):
        pygame.draw.line(surface, color, (x, y0), (min(x + 4, x1), y0))
        pygame.draw.line(surface, color, (x, y1), (min(x + 4, x1), y1))
    for y in range(y0, y1, 8):
        pygame.draw.line(surface, color, (x0, y), (x0, min(y + 4, y1)))
        pygame.draw.line(surface, color, (x1, y), (x1, min(y + 4, y1)))


def inside_any_circle(targets, pos):
    """Ground truth: is the point inside the visible circle of any target?"""
    return any((pos[0] - t.x) ** 2 + (pos[1] - t.y) ** 2 <= t.radius ** 2 for t in targets)


def pick_target(targets, fx, fy):
    """Prefer a target whose aim point is on screen and not inside another
    target's circle, so each shot demonstrates exactly one thing."""
    w, h = WINDOW_SIZE
    for t in targets:
        aim = (t.x + fx * t.radius, t.y + fy * t.radius)
        others = [o for o in targets if o is not t]
        if 0 < aim[0] < w and 60 < aim[1] < h - 40 and not inside_any_circle(others, aim) \
                and not any(o.get_bounding_rect().collidepoint(aim) for o in others):
            return t
    return targets[0]


def main():
    random.seed(7)
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    font = pygame.font.SysFont("consolas", 22)
    small = pygame.font.SysFont("consolas", 17)
    engine = GameEngine()
    video = VideoWriter(OUT, WINDOW_SIZE)

    shot_gap = int(DURATION * FPS / (len(SHOTS) + 0.3))
    cursor = (350.0, 250.0)
    move_from, move_to = cursor, cursor
    pending = None          # (target, shot) being aimed at
    caption, caption_color = "BEFORE changes: starter code (hit-detection bug present)", (255, 255, 255)
    flash = 0.0

    for frame in range(int(DURATION * FPS)):
        i, phase = divmod(frame, shot_gap)
        if phase == 0 and i < len(SHOTS):
            kind, (fx, fy), _ = SHOTS[i]
            target = pick_target(engine.targets, fx, fy)
            aim = (target.x + fx * target.radius, target.y + fy * target.radius)
            pending = (target, SHOTS[i], aim)
            move_from, move_to = cursor, aim
        travel = shot_gap * 0.55
        if pending:
            cursor = lerp(move_from, move_to, min(1.0, phase / travel))
            if phase == int(travel) + 2:
                target, (kind, _, _), aim = pending
                expected = "HIT" if inside_any_circle(engine.targets, aim) else "MISS"
                before = engine.hits
                engine.handle_click((int(aim[0]), int(aim[1])))
                got = "HIT" if engine.hits > before else "MISS"
                ok = got == expected
                caption = f"Click {kind}: should be {expected}, game says {got}" + ("" if ok else "  <-- BUG")
                caption_color = (140, 230, 140) if ok else (255, 110, 90)
                flash = 1.0
                pending = None

        engine.update()
        engine.draw(screen, font)
        for t in engine.targets:
            dashed_rect(screen, t.get_bounding_rect(), (255, 220, 80))
        screen.blit(small.render("dashed square = game's actual hitbox (debug overlay)", True, (255, 220, 80)), (10, 40))
        draw_cursor(screen, cursor, flash)
        flash = max(0.0, flash - 0.06)
        draw_caption(screen, small, caption, caption_color)
        video.write(screen)

    video.close()
    pygame.quit()
    print(f"wrote {os.path.abspath(OUT)} ({video.frames} frames @ {FPS} fps)")


if __name__ == "__main__":
    main()
