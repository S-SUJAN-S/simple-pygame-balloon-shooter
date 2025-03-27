import pygame
import random
import sys
import os

# Initialize Pygame & Mixer
pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error:
    print("Warning: Pygame mixer could not be initialized. Running without sound.")
    sound_enabled = False

# Screen dimensions
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Balloon Shooter - Select Difficulty")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
YELLOW = (255, 220, 0) # For Medium button maybe
ORANGE = (255, 140, 0) # For Hard button maybe

# Attractive colors for balloons
attractive_colors = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 165, 0),
    (128, 0, 128), (255, 255, 0), (0, 255, 255),
]

# --- Game Assets ---
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 36)
font_tiny = pygame.font.SysFont(None, 24)

# Sounds (Load with error handling - using your provided paths)
shoot_sound = None
pop_sound = None
if sound_enabled:
    try:
        shoot_sound = pygame.mixer.Sound("shoot.wav")
    except:
        print("Warning: Could not load shoot.wav")
    try:
        pop_sound = pygame.mixer.Sound("pop.wav")
    except:
        print("Warning: Could not load pop.wav")

# High score file
HIGH_SCORE_FILE = "highscore.txt"

# --- Game Settings ---
FPS = 60
INITIAL_SHOOTER_SPEED = 7 # Can still be adjusted by player
BULLET_SPEED = 10
INITIAL_LIVES = 5

# --- NEW: Difficulty Levels ---
DIFFICULTY_LEVELS = {
    "Easy":   {'spawn_delay': 1800, 'min_speed': 1.5, 'max_speed': 3.0, 'score_multiplier': 1.0, 'color': GREEN},
    "Medium": {'spawn_delay': 1300, 'min_speed': 2.0, 'max_speed': 4.5, 'score_multiplier': 1.5, 'color': YELLOW},
    "Hard":   {'spawn_delay': 800,  'min_speed': 3.0, 'max_speed': 6.0, 'score_multiplier': 2.0, 'color': ORANGE}
}

# --- Balloon Properties ---
BALLOON_TYPES = {
    'small':  {'radius': 15, 'base_score': 3},
    'medium': {'radius': 20, 'base_score': 2},
    'large':  {'radius': 27, 'base_score': 1},
}
BALLOON_PROBABILITY = {'small': 0.3, 'medium': 0.5, 'large': 0.2}
balloon_type_keys = list(BALLOON_TYPES.keys())
balloon_probabilities = [BALLOON_PROBABILITY[key] for key in balloon_type_keys]

# --- Shooter properties ---
shooter_width = 50
shooter_height = 20
shooter_x = WIDTH // 2 - shooter_width // 2
shooter_y = HEIGHT - shooter_height - 10

# --- Bullet properties ---
bullet_width = 5
bullet_height = 10

# --- Game State Variables ---
game_state = "start" # "start", "playing", "paused", "game_over"
score = 0
high_score = 0
lives = INITIAL_LIVES
shooter_speed = INITIAL_SHOOTER_SPEED
selected_difficulty = None # NEW: Store the chosen difficulty name
# These will be set based on selected_difficulty
balloon_spawn_delay = 0
balloon_min_speed = 0
balloon_max_speed = 0
score_multiplier = 1.0

# --- Lists for game objects ---
bullets = []
balloons = []

# --- Clock ---
clock = pygame.time.Clock()

# --- Custom Events ---
SPAWN_BALLOON = pygame.USEREVENT + 1

# --- Button Class --- (Same as before)
class Button:
    def __init__(self, text, rect, base_color, hover_color, font, action=None):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.base_color = base_color
        self.hover_color = hover_color
        self.font = font
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=10) # Outline
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                self.action()
            return True
        return False

# --- Utility Functions --- (load/save high score, display_text, draw_multiline_text) ---
def load_high_score():
    global high_score
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                high_score = int(f.read())
        else:
             high_score = 0
    except (IOError, ValueError):
        print(f"Warning: Could not read or parse {HIGH_SCORE_FILE}. Resetting high score.")
        high_score = 0

def save_high_score():
    global high_score
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(high_score))
    except IOError:
        print(f"Warning: Could not save high score to {HIGH_SCORE_FILE}.")

def display_text(text, font, color, center):
    message = font.render(text, True, color)
    rect = message.get_rect(center=center)
    screen.blit(message, rect)

def draw_multiline_text(surface, text, pos, font, color, line_spacing=1.2):
    lines = text.split('\n')
    x, y = pos
    line_height = font.get_linesize() * line_spacing
    for line in lines:
        line_surface = font.render(line, True, color)
        line_rect = line_surface.get_rect(topleft=(x, y))
        surface.blit(line_surface, line_rect)
        y += line_height

def quit_game():
    print("Quitting game...")
    save_high_score()
    pygame.quit()
    sys.exit()

def reset_game():
    # ONLY resets score, lives, shooter position, and object lists
    global score, lives, shooter_x, bullets, balloons, shooter_speed
    print("Resetting game state (score, lives, position)...")
    score = 0
    lives = INITIAL_LIVES
    shooter_x = WIDTH // 2 - shooter_width // 2
    bullets = []
    balloons = []
    shooter_speed = INITIAL_SHOOTER_SPEED # Reset player-adjustable speed

# --- NEW: Function to start the game with selected difficulty ---
def start_game(difficulty_name):
    global selected_difficulty
    print(f"Starting game with difficulty: {difficulty_name}")
    selected_difficulty = difficulty_name
    change_state("playing")

# --- Modified change_state function ---
def change_state(new_state):
    # --- Declare ALL globals modified in this function at the TOP ---
    global game_state, balloon_spawn_delay, balloon_min_speed, balloon_max_speed
    global score_multiplier, selected_difficulty # <--- ADD selected_difficulty HERE

    print(f"Changing state from {game_state} to {new_state}")

    # Stop timer regardless of new state, will be restarted if needed
    pygame.time.set_timer(SPAWN_BALLOON, 0)

    if new_state == "playing":
        # If starting fresh (from start or game over)
        if game_state == "start" or game_state == "game_over":
            if selected_difficulty is None:
                print("Error: No difficulty selected!")
                return # Don't start playing

            reset_game() # Reset score, lives, etc.

            # Apply difficulty settings
            params = DIFFICULTY_LEVELS[selected_difficulty]
            balloon_spawn_delay = params['spawn_delay']
            balloon_min_speed = params['min_speed']
            balloon_max_speed = params['max_speed']
            score_multiplier = params['score_multiplier']
            print(f"Applied settings for {selected_difficulty}: delay={balloon_spawn_delay}, speed=({balloon_min_speed}-{balloon_max_speed}), score_mult={score_multiplier}")

        # If resuming from pause, parameters are already set, just change state

        game_state = "playing"
        # Start/Resume the balloon spawn timer with the correct delay
        pygame.time.set_timer(SPAWN_BALLOON, int(balloon_spawn_delay))

    elif new_state == "paused":
        if game_state == "playing":
            game_state = "paused"
            # Timer already stopped
        else:
             print(f"Cannot pause from state: {game_state}")
             if game_state == "playing":
                 pygame.time.set_timer(SPAWN_BALLOON, int(balloon_spawn_delay))
             return # Don't change state

    elif new_state == "game_over":
        game_state = "game_over"
        # Timer already stopped
        global high_score # Need global here ONLY if assigning (we are, indirectly via save)
        if score > high_score:
            print(f"New high score: {score}")
            high_score = score
            save_high_score()

    elif new_state == "start":
        game_state = "start"
        # Timer already stopped
        # Reset selected difficulty for next choice
        selected_difficulty = None # Now this assignment is valid because global was declared above
        # --- REMOVE the redundant global declaration from here ---
        # global selected_difficulty

    else:
         game_state = new_state

# --- Button Instances ---
button_width = 150 # Slightly smaller buttons for difficulty
button_height = 50
button_y = HEIGHT - 150
spacing = 20

# Difficulty Buttons
easy_button = Button("Easy",
                     (WIDTH // 2 - (button_width * 1.5 + spacing), button_y, button_width, button_height),
                     DIFFICULTY_LEVELS["Easy"]["color"], LIGHT_GRAY, font_medium,
                     action=lambda: start_game("Easy")) # Use start_game function

medium_button = Button("Medium",
                       (WIDTH // 2 - button_width // 2, button_y, button_width, button_height),
                       DIFFICULTY_LEVELS["Medium"]["color"], LIGHT_GRAY, font_medium,
                       action=lambda: start_game("Medium"))

hard_button = Button("Hard",
                     (WIDTH // 2 + button_width // 2 + spacing, button_y, button_width, button_height),
                     DIFFICULTY_LEVELS["Hard"]["color"], LIGHT_GRAY, font_medium,
                     action=lambda: start_game("Hard"))

# Other Buttons
font_small = pygame.font.Font(None, 36)  # Adjust the font size

restart_button = Button("New Game",
                        (WIDTH // 2 - button_width // 2, HEIGHT // 2 + (button_height // 2 - 20), button_width, button_height),
                        GREEN, LIGHT_GRAY, font_small,  # Use smaller font
                        action=lambda: change_state("start"))

quit_button_game_over = Button("Quit",
                        (WIDTH // 2 - button_width // 2, HEIGHT // 2 + (button_height // 2 + 60), button_width, button_height),
                        RED, LIGHT_GRAY, font_small, action=quit_game)


resume_button = Button("Resume (P)",
                       (WIDTH // 2 - (button_width + 40) // 2, HEIGHT // 2 - (button_height + 10), button_width + 40, button_height),
                       GREEN, LIGHT_GRAY, font_medium, action=lambda: change_state("playing"))

quit_button_pause = Button("Quit (ESC)",
                           (WIDTH // 2 - (button_width + 40) // 2, HEIGHT // 2 + (button_height - 25), button_width + 40, button_height),
                           RED, LIGHT_GRAY, font_medium, action=quit_game)


difficulty_buttons = [easy_button, medium_button, hard_button] # Group for easier handling

# --- Drawing Functions --- (draw_shooter, draw_bullet, draw_balloon are the same)
def draw_shooter(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, shooter_width, shooter_height), border_radius=5)
    cannon_rect = pygame.Rect(x + shooter_width // 2 - 3, y - 5, 6, 5)
    pygame.draw.rect(screen, BLUE, cannon_rect)

def draw_bullet(bullet_rect):
    pygame.draw.rect(screen, BLACK, bullet_rect)

def draw_balloon(balloon):
    radius = balloon['radius']
    pygame.draw.circle(screen, balloon['color'], (balloon['x'], balloon['y']), radius)
    knot_offset = radius * 0.25
    knot_height = radius * 0.4
    points = [
        (balloon['x'] - knot_offset, balloon['y'] + radius),
        (balloon['x'] + knot_offset, balloon['y'] + radius),
        (balloon['x'], balloon['y'] + radius + knot_height)
    ]
    pygame.draw.polygon(screen, balloon['color'], points)
    shine_radius = int(radius * 0.2)
    shine_offset = int(radius * 0.4)
    shine_center = (balloon['x'] + shine_offset, balloon['y'] - shine_offset)
    pygame.draw.circle(screen, WHITE, shine_center, shine_radius)


# --- Screen Drawing Functions ---
def draw_start_screen():
    screen.fill(WHITE)
    display_text("Balloon Shooter", font_large, BLACK, (WIDTH // 2, 100)) # Simpler title
    display_text(f"High Score: {high_score}", font_medium, BLUE, (WIDTH // 2, 180))

    instructions = (
        "How to Play:\n\n"
        "- Use LEFT/RIGHT arrows to move.\n"
        "- Press SPACE to shoot.\n"
        "- Pop balloons before they fall.\n"
        "- UP/DOWN arrows change shooter speed.\n"
        "- Different sizes = different points!\n"
        "- Higher difficulty = more points!\n\n"
        "Shortcuts: P = Pause | ESC = Quit"
    )
    draw_multiline_text(screen, instructions, (50, 250), font_small, BLACK)

    display_text("Select Difficulty:", font_medium, BLACK, (WIDTH // 2, HEIGHT - 180))
    # Draw difficulty buttons
    for button in difficulty_buttons:
        button.draw(screen)

    pygame.display.flip()

def draw_game_screen():
    screen.fill(WHITE)
    draw_shooter(shooter_x, shooter_y)
    for bullet in bullets:
        draw_bullet(bullet)
    for balloon in balloons:
        draw_balloon(balloon)

    # Draw HUD
    display_text(f"Score: {score}", font_small, BLACK, (80, 30))
    lives_text = font_small.render("Lives:", True, BLACK)
    lives_rect = lives_text.get_rect(topright=(WIDTH - 130, 15))
    screen.blit(lives_text, lives_rect)
    for i in range(lives):
         heart_x = WIDTH - 110 + (i * 25)
         pygame.draw.circle(screen, RED, (heart_x, 30), 10)

    display_text(f"Speed: {shooter_speed}", font_small, BLACK, (WIDTH // 2, 30))
    # Display selected difficulty instead of level
    if selected_difficulty:
        display_text(f"Difficulty: {selected_difficulty}", font_small, BLACK, (WIDTH // 2, 60))

    pygame.display.flip()

def draw_pause_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((128, 128, 128, 180))
    screen.blit(overlay, (0, 0))
    display_text("Paused", font_large, BLACK, (WIDTH // 2, HEIGHT // 2 - 100))
    resume_button.draw(screen)
    quit_button_pause.draw(screen)
    display_text("Press P to Resume or ESC to Quit", font_tiny, BLACK, (WIDTH // 2, HEIGHT // 2 + 100))
    pygame.display.flip()

def draw_game_over_screen():
    screen.fill(GRAY)
    display_text("Game Over!", font_large, RED, (WIDTH // 2, HEIGHT // 2 - 200))
    display_text(f"Final Score: {score}", font_medium, BLACK, (WIDTH // 2, HEIGHT // 2 - 130))
    if selected_difficulty:
         display_text(f"(Difficulty: {selected_difficulty})", font_small, BLACK, (WIDTH // 2, HEIGHT // 2 - 50))

    is_new_high = score > high_score and score > 0
    final_high_score = max(score, high_score) if is_new_high else high_score

    if is_new_high:
         display_text(f"New High Score!", font_medium, BLUE, (WIDTH // 2, HEIGHT // 2 + 210))
         display_text(f"High Score: {final_high_score}", font_small, BLACK, (WIDTH // 2, HEIGHT // 2 + 250))
    else:
         display_text(f"High Score: {final_high_score}", font_small, BLACK, (WIDTH // 2, HEIGHT // 2 + 250))

    restart_button.draw(screen) # Button now says "New Game" and goes to start screen
    quit_button_game_over.draw(screen)
    pygame.display.flip()

# --- Game Logic Update Function --- (Removed update_difficulty call)
def run_game_logic():
    global shooter_x, score, lives, game_state

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and shooter_x > 0:
        shooter_x -= shooter_speed
    if keys[pygame.K_RIGHT] and shooter_x < WIDTH - shooter_width:
        shooter_x += shooter_speed

    for bullet in bullets[:]:
        bullet.y -= BULLET_SPEED
        if bullet.y < 0:
            bullets.remove(bullet)

    for balloon in balloons[:]:
        balloon['y'] += balloon['speed']
        radius = balloon['radius']

        if balloon['y'] > HEIGHT + radius:
            lives -= 1
            balloons.remove(balloon)
            print(f"Balloon missed! Lives left: {lives}")
            if lives < 0:
                change_state("game_over")
            continue

        balloon_center_x, balloon_center_y = balloon['x'], balloon['y']
        balloon_rect = pygame.Rect(balloon_center_x - radius, balloon_center_y - radius, radius * 2, radius * 2)

        for bullet in bullets[:]:
            if balloon_rect.colliderect(bullet):
                dx = balloon_center_x - bullet.centerx
                dy = balloon_center_y - bullet.centery
                distance_sq = dx*dx + dy*dy
                if distance_sq < (radius + bullet.width)**2:
                    # Calculate score based on balloon type and difficulty multiplier
                    score_to_add = int(balloon['base_score'] * score_multiplier) # Apply multiplier
                    score += score_to_add

                    bullets.remove(bullet)
                    balloons.remove(balloon)
                    if sound_enabled and pop_sound:
                        pop_sound.play()
                    # REMOVED call to update_difficulty() here
                    break

# --- Main Game Loop ---
load_high_score()
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        # --- State-DEPENDENT Event Handling ---
        if game_state == "start":
            # Handle difficulty button clicks
            for button in difficulty_buttons:
                button.check_hover(mouse_pos)
                button.handle_click(event) # Action (start_game) handled by button

        elif game_state == "playing":
            if event.type == SPAWN_BALLOON:
                chosen_type_key = random.choices(balloon_type_keys, weights=balloon_probabilities, k=1)[0]
                balloon_info = BALLOON_TYPES[chosen_type_key]
                radius = balloon_info['radius']
                base_score = balloon_info['base_score']

                balloon = {
                    'x': random.randint(radius, WIDTH - radius),
                    'y': -radius,
                    # Use speeds set by difficulty
                    'speed': random.uniform(balloon_min_speed, balloon_max_speed),
                    'color': random.choice(attractive_colors),
                    'radius': radius,
                    'base_score': base_score
                }
                balloons.append(balloon)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet_rect = pygame.Rect(shooter_x + shooter_width // 2 - bullet_width // 2,
                                                shooter_y - bullet_height, bullet_width, bullet_height)
                    bullets.append(bullet_rect)
                    if sound_enabled and shoot_sound:
                        shoot_sound.play()
                elif event.key == pygame.K_UP:
                    shooter_speed += 1
                elif event.key == pygame.K_DOWN:
                    shooter_speed = max(1, shooter_speed - 1)
                elif event.key == pygame.K_p:
                    change_state("paused")

        elif game_state == "paused":
            resume_button.check_hover(mouse_pos)
            quit_button_pause.check_hover(mouse_pos)
            resume_button.handle_click(event)
            quit_button_pause.handle_click(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                 change_state("playing")

        elif game_state == "game_over":
            restart_button.check_hover(mouse_pos) # Button now says "New Game"
            quit_button_game_over.check_hover(mouse_pos)
            restart_button.handle_click(event) # Action now goes to "start" state
            quit_button_game_over.handle_click(event)

    # --- Game Logic & Drawing based on State ---
    if game_state == "start":
        draw_start_screen()
    elif game_state == "playing":
        run_game_logic()
        draw_game_screen()
    elif game_state == "paused":
        draw_pause_screen()
    elif game_state == "game_over":
        draw_game_over_screen()

    # --- Frame Rate Control ---
    clock.tick(FPS)

# --- Cleanup ---
quit_game()