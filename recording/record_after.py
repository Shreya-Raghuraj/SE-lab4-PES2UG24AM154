"""
Records Lab-4/videos/after.mp4: 10 s of the FINISHED game.

Timeline (30 fps):
  0.0 - 4.5 s  real-time play: hits build the combo, an edge hit on a
               moving target counts, a click just outside an edge is a
               miss and resets the combo
  4.5 - 6.1 s  fast-forward (x15, labelled on screen) to the last 2 s
  6.1 - 8.1 s  real-time play until the 30 s timer reaches zero
  8.1 - 9.3 s  round over: final score shown, a click is ignored
  9.3 -10.0 s  R pressed: new round with score, combo and timer reset
"""

import math
import os
import random

from recorder import FPS, VideoWriter, draw_caption, draw_cursor, pygame

from game.game_engine import GameEngine
from game.renderer import WINDOW_SIZE

OUT = os.path.join(os.path.dirname(__file__), "..", "videos", "after.mp4")
DT = 1.0 / FPS
FF_SPEED = 15

# (offset from centre in radii, description); None offset = empty space
SHOTS_1 = [
    ((0.0, 0.0), "centre"), ((0.2, -0.3), "inside"), ((0.0, 0.0), "centre"),
    ((-0.8, 0.0), "inside left edge"), ((1.2, 0.0), "just outside right edge"),
    ((0.0, 0.0), "centre"),
]
SHOTS_2 = [((0.0, 0.0), "centre"), ((0.3, 0.3), "inside"), ((0.0, 0.8), "inside bottom edge")]


def inside_any_circle(targets, pos):
    return any((pos[0] - t.x) ** 2 + (pos[1] - t.y) ** 2 <= t.radius ** 2 for t in targets)


class Shooter:
    """Moves the on-screen cursor onto a (moving) target and clicks."""

    def __init__(self):
        self.cursor = (350.0, 270.0)
        self.flash = 0.0
        self.caption = ""
        self.color = (255, 255, 255)

    def aim_point(self, target, offset):
        return (target.x + offset[0] * target.radius, target.y + offset[1] * target.radius)

    def play(self, engine, shots, frames, render):
        per_shot = frames // len(shots)
        for offset, kind in shots:
            others_free = [t for t in engine.targets
                           if not inside_any_circle([o for o in engine.targets if o is not t],
                                                    self.aim_point(t, offset))]
            target = min(others_free or engine.targets,
                         key=lambda t: math.dist(self.cursor, (t.x, t.y)))
            if "edge" in kind:  # use the fastest target for edge shots
                target = max(others_free or engine.targets, key=lambda t: math.hypot(t.vx, t.vy))
            for f in range(per_shot):
                aim = self.aim_point(target, offset)
                k = min(1.0, (f + 1) / (per_shot * 0.6))
                self.cursor = (self.cursor[0] + (aim[0] - self.cursor[0]) * k,
                               self.cursor[1] + (aim[1] - self.cursor[1]) * k)
                if f == int(per_shot * 0.6):
                    self.click(engine, kind)
                engine.update(DT)
                render()

    def click(self, engine, kind):
        pos = (int(self.cursor[0]), int(self.cursor[1]))
        should_hit = inside_any_circle(engine.targets, pos)
        score, mult = engine.score, engine.multiplier
        engine.handle_click(pos)
        self.flash = 1.0
        if engine.score > score:
            self.caption = f"Click {kind}: HIT  +{engine.score - score} pts (x{mult})  -> combo x{engine.multiplier}"
            self.color = (140, 230, 140)
        else:
            self.caption = f"Click {kind}: MISS -> combo reset to x{engine.multiplier}"
            self.color = (255, 170, 120)
        assert (engine.score > score) == should_hit, "hit detection disagrees with the circle"


def main():
    random.seed(11)
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    font = pygame.font.SysFont("consolas", 22)
    small = pygame.font.SysFont("consolas", 17)
    engine = GameEngine()
    video = VideoWriter(OUT, WINDOW_SIZE)
    shooter = Shooter()
    shooter.caption = "AFTER changes: moving targets, combo scoring, 30 s round"

    def render(cursor=True):
        engine.draw(screen, font)
        if cursor:
            draw_cursor(screen, shooter.cursor, shooter.flash)
        shooter.flash = max(0.0, shooter.flash - 0.08)
        draw_caption(screen, small, shooter.caption, shooter.color)
        video.write(screen)

    # 1) real-time play
    shooter.play(engine, SHOTS_1, int(4.5 * FPS), render)

    # 2) fast-forward to 2 s left, labelled
    shooter.caption, shooter.color = f">> fast-forward x{FF_SPEED} to the end of the 30 s round", (255, 220, 80)
    while engine.time_left > 2.0 + FF_SPEED * DT:
        for _ in range(FF_SPEED):
            engine.update(DT)
        render(cursor=False)
    while engine.time_left > 2.0:
        engine.update(DT)

    # 3) real-time until the timer runs out
    shooter.play(engine, SHOTS_2, int(1.5 * FPS), render)
    while not engine.round_over:
        engine.update(DT)
        render()

    # 4) round over: a click is ignored
    for f in range(int(1.2 * FPS)):
        if f == int(0.5 * FPS):
            before = (engine.score, engine.hits, engine.misses)
            engine.handle_click((int(shooter.cursor[0]), int(shooter.cursor[1])))
            assert (engine.score, engine.hits, engine.misses) == before
            shooter.flash = 1.0
            shooter.caption, shooter.color = "Click after time's up: ignored (score unchanged)", (255, 220, 80)
        engine.update(DT)
        render()

    # 5) press R -> new round
    engine.handle_key(pygame.K_r)
    shooter.caption, shooter.color = "R pressed: new round - score, combo and timer reset", (140, 230, 140)
    for _ in range(int(0.7 * FPS)):
        engine.update(DT)
        render()

    video.close()
    pygame.quit()
    print(f"wrote {os.path.abspath(OUT)} ({video.frames} frames = {video.frames / FPS:.1f} s @ {FPS} fps)")


if __name__ == "__main__":
    main()
