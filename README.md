# **TETRIS GAME** 🟦🟥🟩🟨🟪🟧


## Create and activate a virtual environment 🌐(recommended)

```sh
python --version
```


## Windows 💻

```sh 
python -m venv .venv
.venv\Scripts\activate
```


## MacOS/Linux 🍎/🐧

```sh 
python3 -m venv .venv
source .venv/bin/activate
```


## Install dependency✅

```sh 
pip install pygame
```


## Save the game file in this folder as: 📁

```sh 
tetris.py
```


- *** Paste the full Tetris script into that file. ***
- *** Run the game 💻***
  
```sh
python tetris.py
```


## If macOS/Linux 🍎/🐧

```sh 
python3 tetris_fullscreen_no_overlap.py
```


## Controls🎮
- Left/Right: Move
- Down: Soft drop
- Up or X: Rotate clockwise
- Z: Rotate counterclockwise
- Space: Hard drop
- C: Hold piece
- P: Pause/Resume
- R: Restart
- Esc: Quit
- Mouse: Click Restart / Exit buttons

## Notes 📝
- Runs fullscreen and auto-scales to prevent overlap.
- Shows only the next 3 pieces (smaller size).
- Scoreboard displays High score and recent scores (numbers only).
- A scores file (tetris_scores.json) is created automatically after the first completed run.
