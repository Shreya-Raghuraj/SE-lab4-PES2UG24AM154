"""
hit_detection: figures out whether a click landed on a target.
"""


def is_inside_circle(target, click_pos):
    """True if click_pos lies inside (or on the edge of) the target's
    visible circle. (target.x, target.y) is the circle's CENTER."""
    dx = click_pos[0] - target.x
    dy = click_pos[1] - target.y
    return dx * dx + dy * dy <= target.radius * target.radius


def check_hit(targets, click_pos):
    """
    Returns the target that was clicked, or None if the click missed
    every target.

    Uses the target's real circular shape instead of a bounding box.
    Targets are checked last-drawn first, so when two overlap the one
    on top wins.
    """
    for target in reversed(targets):
        if is_inside_circle(target, click_pos):
            return target
    return None
