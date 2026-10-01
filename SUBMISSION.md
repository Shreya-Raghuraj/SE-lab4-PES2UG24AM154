# Lab 4 – Vibe Coding: Target Shooting

**SRN:** PES2UG24AM154
**Assigned repo:** [SETAPESU26/04_target_shooting](https://github.com/SETAPESU26/04_target_shooting) (starter commit `1a0c3aa`)

## Deliverables in this folder

| Deliverable | Location |
|---|---|
| a. Videos (before / after) | `videos/before.mp4`, `videos/after.mp4` (10 s each, 700×500, 30 fps) |
| b. Updated code | `target-shooting/` |
| c. Chat history | *add the exported chat PDF here* |

The original lab README is kept as `README.md`.

## What changed (one commit per task)

| Task | Change | Files |
|---|---|---|
| 1. Hit-detection bug | `check_hit` now tests the squared distance from the click to the target **center** against `radius²` instead of a rect whose top-left corner was wrongly placed at the center. Overlapping targets: the one drawn on top wins. `get_bounding_rect` is also centered correctly. | `game/hit_detection.py`, `game/target.py` |
| 2. Moving targets | Three target kinds: **slow** straight (90 px/s, red), **fast** straight (200 px/s, orange), and **wave** (130 px/s, purple; weaves side to side). All of them bounce off the edges of the play area below the HUD. Movement uses the frame `dt`, so speed doesn't depend on frame rate. | `game/target.py`, `game/game_engine.py`, `game/renderer.py`, `main.py` |
| 3. Combo scoring | Each hit scores `10 × multiplier`. The multiplier starts at x1 and goes up by 1 per consecutive hit, up to x5. A miss resets it to x1. The HUD shows the score and the combo (the combo text gets warmer in color as it grows). | `game/game_engine.py`, `game/renderer.py` |
| 4. 30 s round | The countdown appears in the HUD and turns red for the last 5 s. At 0, targets freeze, clicks are ignored, and an overlay shows the final score, hits, misses and accuracy. **R** or **SPACE** starts a new round with score, combo and timer reset. | `game/game_engine.py`, `game/renderer.py`, `main.py` |

## Running the game

```bash
cd Lab-4/target-shooting
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Controls: left-click a target to shoot it. After the round ends, press R or SPACE to play again.

## How the videos were made

The videos come from the real game code, not mock-ups. `recording/record_before.py` and
`recording/record_after.py` run the game's `GameEngine` headless and send scripted mouse
clicks to `handle_click`, the same way `main.py` does. Every frame the game draws is piped
to ffmpeg. A crosshair and a caption bar are drawn on top so you can see where each click
landed and what the game decided.

- **before.mp4**: unmodified starter code. The dashed yellow squares are a debug overlay of the buggy hitbox. Clicks inside a target's upper-left edge register as **MISS**, and clicks clearly outside its lower-right edge register as **HIT**.
- **after.mp4**: finished game. Moving targets are hit at their center and at their edges, a near-miss resets the combo, and the score climbs with the multiplier. The middle part is a clearly labelled x15 fast-forward to the last 2 s of the round. After that the timer reaches 0, the final score is shown, a click after time-up is ignored, and pressing R starts a fresh round.

To regenerate the videos: `pip install pygame imageio-ffmpeg`, then run either script from `recording/`. `record_before.py` needs the starter code checked out (`git checkout <starter commit> -- Lab-4/target-shooting`).
