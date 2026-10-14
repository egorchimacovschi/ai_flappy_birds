# AI_FLAPPY_BIRDS

A Flappy-Bird clone built in pygame: click to flap, with an animated bird, procedurally spawned pipes, scoring, and a restart screen.

This is currently a fully playable game controlled by mouse clicks. A planned next step is adding an AI mode where a NEAT-trained neural network flies the bird itself, with its network drawn live on screen.

## 📁 What's Inside

| Path | Content |
|---|---|
| `flappy_birds.py` | Entry point and main `Game` class: window setup, the game loop, spawning/scrolling pipes, scoring, collision detection, and the game-over/restart flow |
| `scripts/bird.py` | `Bird` sprite — gravity, click-to-flap, a 3-frame flap animation (`bird1.png`/`bird2.png`/`bird3.png`), and rotating the sprite based on velocity |
| `scripts/pipe.py` | `Pipe` sprite — a single top or bottom pipe that scrolls left and removes itself once off-screen |
| `scripts/button.py` | A small reusable `Button` class, used for the restart button on the game-over screen |
| `data/img/` | Art assets — see below |
| `flappybirds.zip` | A zipped snapshot of an earlier version of this project |

### `data/img/` assets

| File | Used for |
|---|---|
| `bg.png` | Background |
| `ground.png` | Scrolling floor strip |
| `bird1.png`, `bird2.png`, `bird3.png` | Flap animation frames |
| `pipe.png` | Pipe sprite (flipped for the top pipe) |
| `restart.png` | Restart button on the game-over screen |
| `bglong.png`, `spritesheet.png` | Not currently loaded by the code — likely reserved for a future revision (e.g. a longer scrolling background, or a single sprite sheet instead of separate bird frames) |

## ⚙️ Requirements

```bash
pip install pygame
```

## 🚀 Running

Run it from inside this folder — assets are loaded using paths relative to here (`./data/img/...`):

```bash
cd Projects/AI_FLAPPY_BIRDS
python3 flappy_birds.py
```

## 🎮 Controls

| Input | Action |
|---|---|
| Left mouse click | Flap / start the game / restart after game over |

## 📌 Notes

- Score increases by 1 each time the bird fully passes a pipe.
- The game ends if the bird hits a pipe, the ground, or the top of the screen; clicking the restart button resets the bird, pipes, and score.
