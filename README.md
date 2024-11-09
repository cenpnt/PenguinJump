# PenguinJump Game

## Overview

**PenguinJump** is a 2D platformer game developed with Pygame. The game follows the Singleton design pattern and includes key features such as player movement, camera control, level management, and basic UI elements for a fun and engaging experience.

## Table of Contents
- [Installation](#installation)
- [Gameplay](#gameplay)
- [Class Structure](#class-structure)
  - [Game Class](#game-class)
  - [Enemy Class](#enemy-class)
  - [Player Class](#player-class)
  - [Bullet Class](#bullet-class)
  - [Camera Class](#camera-class)
  - [Sprite Class](#sprite-class)
  - [Singleton Class](#singleton-class)
  - [Settings Class](#settings-class)
- [Settings and Customization](#settings-and-customization)
- [License](#license)

## Installation

1. **Clone the Repository:**
    ```bash
    git clone [https://github.com/yourusername/PenguinJump.git](https://github.com/cenpnt/PenguinJump.git)
    ```
2. **Install Requirements:**
   - Ensure you have Python 3.x installed.
   - Install the dependencies:
     ```bash
     pip install -r requirements.txt
     ```
3. **Run the Game:**
   ```bash
   python main.py

## Gameplay

In **PenguinJump**, players control a penguin character navigating upward by jumping across platforms, avoiding enemies, and collecting points. The player can move left or right, jump, and shoot at enemies. As the penguin progresses through levels, the difficulty gradually increases.

## Class Structure

### Game Class
- **Location:** Main game file
- **Inheritance:** Singleton
- **Purpose:** Central game manager that handles game updates, rendering, and user input events.

#### Key Components
- **Initialization:** Sets up display, FPS control, and loads background images and UI elements.
- **Core Game Objects:**
  - **Camera:** Controls game view perspective.
  - **Level:** Manages level generation and structure.
  - **Player:** Manages player actions.
  - **Bullet Group:** Tracks projectiles.
  - **Enemy Instances:** Represents hostile entities.
- **UI Elements:** Score display, game-over message, and restart instructions.

#### Major Methods
- `__init__(self) -> None`: Initializes the game state, display window, game objects, and UI elements.
- `close(self)`: Terminates the game.
- `reset(self)`: Resets the game state, including camera, level, player, and enemies.
- `_event_loop(self)`: Handles user input events like quit and restart.
- `_update_loop(self)`: Updates player, level, and camera positions, and calculates the score.
- `_render_loop(self, camera: Camera)`: Draws background, level, player, and UI elements.
- `run(self)`: Executes the main game loop.

### Enemy Class
- **Purpose:** Represents hostile entities that shoot at the player.

#### Key Properties
- `WIDTH`: 50 pixels - Standard width.
- `HEIGHT`: 15 pixels - Standard height.
- `SHOOT_INTERVAL`: 1000 milliseconds - Time between shots.
- `instances`: List of all active enemy instances.

#### Major Methods
- `__init__(self, parent: Sprite, color=config.GRAY) -> None`: Initializes enemy position and sets up shooting.
- `update(self, camera: Camera) -> None`: Updates enemy position, manages shooting, and checks for bullet collisions.
- `shoot(self) -> None`: Creates bullets and sets their trajectory.
- `draw(self, surface: pygame.Surface, camera: Camera) -> None`: Renders the enemy and its bullets.
- `kill(self) -> None`: Removes enemy and clears bullets.
- `reset(self) -> None`: Resets enemy to its initial state.

#### Collision Handling Methods
- `handle_bullet_collision(self, bullet: Bullet)`: Processes bullet collision events.
- `check_player_bullet_collision(self)`: Detects player bullet collisions.

### Player Class
- **Purpose:** Represents the player's character and handles movement, shooting, and collisions.

#### Key Properties
- `BUTTON_GPIO_PIN`: GPIO pin for firing bullets.
- `last_fire_time`: Tracks the last bullet shot.
- `fire_cooldown`: Delay between bullet shots.
- `bullets`: Group containing bullets fired by the player.
- `gyro_sensor`: MPU6050 sensor for gyroscope movement control.
- `gyro_threshold`: Tilt sensitivity threshold.
- `_jumpforce` and `_bonus_jumpforce`: Configured jump forces.

#### Major Methods
- `init_gyro_sensor(self, retries=3)`: Initializes gyroscope control.
- `read_gyro_input(self)`: Reads gyroscope data to set movement.
- `fire_bullet(self)`: Fires a bullet.
- `update(self, camera: Camera)`: Updates player position and checks for collisions.
- `jump(self, force=None)`: Initiates a jump.
- `collisions(self)`: Checks for collisions with platforms.
- `draw(self, surface: pygame.Surface, camera: Camera)`: Renders the player and bullets.

### Bullet Class
- **Purpose:** Represents projectiles fired by either the player or enemies.

#### Key Properties
- `WIDTH` and `HEIGHT`: Size of the bullet.

#### Major Methods
- `__init__(self, x: int, y: int, speed: int, color, is_player_bullet: bool)`: Initializes bullet properties.
- `update(self, camera: Camera)`: Updates bullet position and checks for screen bounds.
- `set_position(self, penguin_x: int, penguin_y: int)`: Sets bullet starting position.

### Camera Class
- **Purpose:** Manages the game viewport, following the player as they progress.

#### Key Properties
- `state`: Represents the camera’s position.
- `lerp`: Controls camera smoothing.
- `maxheight`: Controls the highest point reached by the player.

#### Major Methods
- `reset(self)`: Resets the camera position.
- `apply_rect(self, rect: Rect) -> Rect`: Applies the camera offset to a given rect.
- `apply(self, target: Sprite) -> Rect`: Offsets a target sprite based on camera position.
- `update(self, target: Rect)`: Follows the target (player).

### Sprite Class
- **Purpose:** Base class for any drawable object like the player, enemies, or bullets.

#### Key Properties
- `color`: Color of the sprite.
- `rect`: Position and dimensions of the sprite.

#### Major Method
- `draw(self, surface: Surface)`: Draws the sprite to the main screen surface.

### Singleton Class
- **Purpose:** Ensures only one instance exists for classes that inherit it, like Game and Camera.

#### Key Mechanism
- `__new__`: Overrides instance creation to control singleton behavior.

### Settings Class
Defines essential game configuration options.

#### Window Settings
- **Resolution**: Width and height of the game window.
- **Display**: Tuple representing the full window size.
- **Frames per Second (FPS)**: Sets the refresh rate.

#### Colors
Defines RGB values for common colors:
- `BLACK`, `WHITE`, `GRAY`: Neutral colors.
- `LIGHT_GREEN`, `ICE`, etc.: Used for bullets, platforms, and player.

#### Player Settings
- **Size**: Player sprite dimensions.
- **Max Speed**: Top movement speed.
- **Jump Forces**: Standard and bonus jump forces.
- **Bullet Speed and Color**: Affects both player and enemy bullets.

#### Platform Settings
- **Platform Color**: Standard and light platform colors.
- **Size**: Dimensions of each platform.
- **Distance Gap**: Min and max platform spacing.
- **Spawn Chances**: Probabilities for special platforms and enemies.

#### Fonts
- **Large Font** and **Small Font**: Configures font sizes for UI elements.

## Settings and Customization

The **Settings** class allows for customization of various gameplay aspects, including player and platform characteristics, colors, and UI fonts.
