"""
recorder: shared helpers for capturing gameplay videos of the real game.

The game runs headless (SDL dummy video driver); every frame the real
GameEngine draws is piped to ffmpeg. Scripted mouse clicks are fed to
the engine exactly like main.py does, and a cursor + caption overlay
is drawn on top so the viewer can see where each click landed.
"""

import os
import subprocess
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import imageio_ffmpeg
import pygame

FPS = 30
GAME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "target-shooting")
sys.path.insert(0, os.path.abspath(GAME_DIR))


class VideoWriter:
    def __init__(self, path, size, fps=FPS):
        self.size = size
        cmd = [
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
            "-r", str(fps), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", path,
        ]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        self.frames = 0

    def write(self, surface):
        self.proc.stdin.write(pygame.image.tobytes(surface, "RGB"))
        self.frames += 1

    def close(self):
        self.proc.stdin.close()
        self.proc.wait()


def draw_cursor(surface, pos, flash=0.0, color=(255, 255, 255)):
    x, y = int(pos[0]), int(pos[1])
    pygame.draw.line(surface, color, (x - 12, y), (x - 4, y), 2)
    pygame.draw.line(surface, color, (x + 4, y), (x + 12, y), 2)
    pygame.draw.line(surface, color, (x, y - 12), (x, y - 4), 2)
    pygame.draw.line(surface, color, (x, y + 4), (x, y + 12), 2)
    pygame.draw.circle(surface, color, (x, y), 2)
    if flash > 0:
        pygame.draw.circle(surface, (255, 255, 120), (x, y), int(6 + 18 * (1 - flash)), 2)


def draw_caption(surface, font, text, color=(255, 255, 255), y_from_bottom=30):
    surf = font.render(text, True, color)
    w, h = surface.get_size()
    bg = pygame.Surface((w, surf.get_height() + 8), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 170))
    surface.blit(bg, (0, h - y_from_bottom - 4))
    surface.blit(surf, ((w - surf.get_width()) // 2, h - y_from_bottom))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
