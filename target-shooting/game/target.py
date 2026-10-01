"""
Target: a circular target the player clicks on. (x, y) is the CENTER
of the circle - this matters for how it's drawn vs. how it's hit-tested.

Targets move: each has a velocity (vx, vy) in pixels/second and a
movement pattern:
  * "straight" - moves in a straight line
  * "wave"     - weaves from side to side around its heading
Both bounce off the edges of the play area.
"""

import math

import pygame


class Target:
    def __init__(self, x, y, radius=28, color=(230, 90, 70), vx=0.0, vy=0.0, pattern="straight"):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = vx
        self.vy = vy
        self.pattern = pattern
        self.age = 0.0

    def get_bounding_rect(self):
        """A square bounding box around the circle - NOT the same
        shape as the actual circle, so it is not used for hit testing.
        (x, y) is the center, so the top-left corner is one radius up
        and to the left of it."""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def velocity(self):
        """Current velocity, including the side-to-side sway for "wave"."""
        if self.pattern != "wave":
            return self.vx, self.vy
        angle = 0.8 * math.sin(self.age * 3.0)
        c, s = math.cos(angle), math.sin(angle)
        return self.vx * c - self.vy * s, self.vx * s + self.vy * c

    def update(self, dt, area):
        """Move for dt seconds and bounce off the edges of `area` (a Rect),
        keeping the whole circle inside it."""
        self.age += dt
        vx, vy = self.velocity()
        self.x += vx * dt
        self.y += vy * dt

        if self.x - self.radius < area.left:
            self.x = area.left + self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > area.right:
            self.x = area.right - self.radius
            self.vx = -abs(self.vx)
        if self.y - self.radius < area.top:
            self.y = area.top + self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius > area.bottom:
            self.y = area.bottom - self.radius
            self.vy = -abs(self.vy)
