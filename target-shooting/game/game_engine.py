"""
GameEngine: owns the targets and handles player clicks.

Targets move around the play area at different speeds / patterns and
respawn elsewhere when hit.
"""

import math
import random

import pygame

from game.target import Target
from game.hit_detection import check_hit
from game.renderer import PLAY_AREA

NUM_TARGETS = 3
TARGET_RADIUS = 28

BASE_POINTS = 10        # points for a hit at x1
MAX_MULTIPLIER = 5      # combo multiplier is capped here
ROUND_SECONDS = 30.0    # length of one shooting round
RESTART_KEYS = (pygame.K_r, pygame.K_SPACE)

# name -> (speed in px/s, movement pattern, color)
TARGET_KINDS = {
    "slow": (90, "straight", (230, 90, 70)),
    "fast": (200, "straight", (240, 170, 50)),
    "wave": (130, "wave", (150, 110, 240)),
}


class GameEngine:
    def __init__(self):
        self.new_round()

    def new_round(self):
        """Start a fresh round: new targets, score/combo/timer all reset."""
        kinds = list(TARGET_KINDS)
        # one of each kind to start, so every movement type is on screen
        self.targets = [self._random_target(kinds[i % len(kinds)]) for i in range(NUM_TARGETS)]
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.streak = 0         # consecutive hits since the last miss
        self.time_left = ROUND_SECONDS
        self.round_over = False

    @property
    def multiplier(self):
        """Combo multiplier for the NEXT hit: x1 with no streak, +1 per
        consecutive hit, capped at MAX_MULTIPLIER."""
        return min(1 + self.streak, MAX_MULTIPLIER)

    def _random_target(self, kind=None):
        kind = kind or random.choice(list(TARGET_KINDS))
        speed, pattern, color = TARGET_KINDS[kind]
        x = random.randint(PLAY_AREA.left + TARGET_RADIUS + 10, PLAY_AREA.right - TARGET_RADIUS - 10)
        y = random.randint(PLAY_AREA.top + TARGET_RADIUS + 10, PLAY_AREA.bottom - TARGET_RADIUS - 10)
        heading = random.uniform(0, 2 * math.pi)
        return Target(x, y, radius=TARGET_RADIUS, color=color,
                      vx=speed * math.cos(heading), vy=speed * math.sin(heading), pattern=pattern)

    def handle_click(self, pos):
        if self.round_over:
            return              # no shots once time is up
        target = check_hit(self.targets, pos)
        if target is not None:
            self.hits += 1
            self.score += BASE_POINTS * self.multiplier
            self.streak += 1
            self.targets.remove(target)
            self.targets.append(self._random_target())
        else:
            self.misses += 1
            self.streak = 0     # a miss resets the combo

    def handle_key(self, key):
        if self.round_over and key in RESTART_KEYS:
            self.new_round()

    def update(self, dt):
        """Advance the game by dt seconds."""
        if self.round_over:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0.0
            self.round_over = True
            return
        for target in self.targets:
            target.update(dt, PLAY_AREA)

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.targets)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Combo: x{self.multiplier}", (175, 10),
                           renderer.combo_color(self.multiplier))
        renderer.draw_text(surface, font, f"Hits {self.hits} / Miss {self.misses}", (310, 10))
        renderer.draw_timer(surface, font, self.time_left)
        if self.round_over:
            renderer.draw_round_over(surface, self.score, self.hits, self.misses)
