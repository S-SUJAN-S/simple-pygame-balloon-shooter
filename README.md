# simple-pygame-balloon-shooter

A classic balloon shooter arcade game made using Python and the Pygame library. Shoot falling balloons to score points, track your high score, and challenge yourself with multiple difficulty levels.

---

### Core Gameplay

Control a shooter at the bottom of the screen. Your objective is to shoot the colorful balloons falling from the top before they reach the ground. Each successfully popped balloon earns you points, contributing to your overall score. Aim carefully and react quickly!

---

### Features

*   **Difficulty Selection:** Choose between Easy, Medium, and Hard modes at the start. This adjusts balloon falling speed, how frequently they appear, and the points awarded, offering varying levels of challenge.
*   **Scoring System:** Different balloon sizes might award different base points. Your score is boosted by a multiplier depending on the selected difficulty level.
*   **Persistent High Score:** The game tracks your highest score achieved. This score is saved locally in a `highscore.txt` file, so you can always strive to beat your personal best.
*   **Lives:** You begin with a limited number of lives. Letting a balloon reach the bottom of the screen costs you one life. The game ends when you run out of lives.
*   **Sound Effects:** Includes basic sound effects for shooting and balloon popping (requires `.wav` files to be present), enhancing the playing experience. *(Optional: Add this point if you are sure the sound files are included)*

---

### How to Run

1.  **Prerequisites:** Make sure you have Python 3 installed.
2.  **Install Pygame:** If you don't have it, open your terminal/command prompt and run: `pip install pygame`
3.  **Download Files:** Download the Python script (`.py`) and any accompanying sound files (`.wav`) from this repository. Keep them in the same directory.
4.  **Execute:** Navigate to that directory in your terminal and run the script using: `python your_script_name.py` (replace `your_script_name.py` with the actual file name).

---

### Controls

*   **Move Shooter:** `LEFT` / `RIGHT` Arrow Keys
*   **Shoot:** `SPACEBAR`
*   **Adjust Shooter Speed:** `UP` / `DOWN` Arrow Keys
*   **Pause/Resume:** `P` Key
*   **Quit Game:** `ESC` Key

---
