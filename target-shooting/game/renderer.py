"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import math

import pygame

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

# Top strip is reserved for the HUD; targets move in the area below it.
HUD_HEIGHT = 44
PLAY_AREA = pygame.Rect(0, HUD_HEIGHT, WIDTH, HEIGHT - HUD_HEIGHT)

COLOR_BG = (25, 25, 35)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD = (40, 40, 55)


def draw_scene(surface, targets):
    surface.fill(COLOR_BG)
    pygame.draw.rect(surface, COLOR_HUD, (0, 0, WIDTH, HUD_HEIGHT))
    for target in targets:
        pygame.draw.circle(surface, target.color, (int(target.x), int(target.y)), target.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(target.x), int(target.y)), target.radius, 2)


def combo_color(multiplier):
    """White at x1, warming up to orange/red as the combo grows."""
    return [(255, 255, 255), (255, 240, 140), (255, 205, 90), (255, 160, 60), (255, 100, 80)][min(multiplier, 5) - 1]


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (255, 220, 80))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)


def draw_timer(surface, font, time_left):
    """Seconds remaining, top-right; turns red for the last 5 seconds."""
    secs = math.ceil(time_left)
    color = (255, 90, 90) if secs <= 5 else COLOR_TEXT
    surf = font.render(f"Time: {secs:2d}s", True, color)
    surface.blit(surf, (WIDTH - surf.get_width() - 10, 10))


def draw_round_over(surface, score, hits, misses):
    """Dimmed overlay with the final score once the round has ended."""
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 170))
    surface.blit(shade, (0, 0))
    shots = hits + misses
    accuracy = 100 * hits / shots if shots else 0
    lines = [
        ("TIME'S UP!", 48, (255, 220, 80)),
        (f"Final score: {score}", 40, COLOR_TEXT),
        (f"Hits: {hits}   Misses: {misses}   Accuracy: {accuracy:.0f}%", 22, (200, 200, 210)),
        ("Press R or SPACE to start a new round", 22, (140, 230, 140)),
    ]
    y = HEIGHT // 2 - 95
    for text, size, color in lines:
        surf = pygame.font.SysFont("consolas", size, bold=size > 30).render(text, True, color)
        surface.blit(surf, surf.get_rect(midtop=(WIDTH // 2, y)))
        y += surf.get_height() + 18
