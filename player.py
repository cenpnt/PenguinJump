from math import copysign
import pygame
from pygame.math import Vector2
from pygame.locals import KEYDOWN, K_SPACE
from pygame.sprite import collide_rect
from pygame.event import Event
from camera import Camera
from singleton import Singleton
from sprite import Sprite
from level import Level
from bullet import Bullet
from enemy import Enemy
import settings as config
import smbus
import time
import RPi.GPIO as GPIO

# Return the sign of a number: getsign(-5) -> -1
getsign = lambda x : copysign(1, x)

# GPIO setup
BUTTON_GPIO_PIN = 17  # GPIO pin number for the button; adjust as needed

GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
GPIO.setup(BUTTON_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

if GPIO.input(BUTTON_GPIO_PIN) == GPIO.HIGH:
	print("test shooting")


class Player(Sprite, Singleton):
    def __init__(self, *args):
        # calling default Sprite constructor
        Sprite.__init__(self, *args)
        
        # Initialize the gyro sensor with retry mechanism
        self.gyro_sensor = None
        self.init_gyro_sensor()
        
        self.last_fire_time = 0  # Track the time of the last bullet fired
        self.fire_cooldown = 0.3
        self.button_pressed = False
        self.last_button_press_time = 0
        self.button_press_delay = 0.2  # Delay in seconds between button presses
        
        # Rest of your initialization code remains the same
        self._image_right = pygame.image.load("./images/penguin-right.png").convert_alpha()
        self._image_right = pygame.transform.scale(self._image_right, (60, 60))
        self._image_left = pygame.image.load("./images/penguin-left.png").convert_alpha()
        self._image_left = pygame.transform.scale(self._image_left, (60, 60))
        self._image = self._image_right  # Start facing right

        self.bullets = pygame.sprite.Group()
        self._rect = self._image.get_rect()
        self.__startrect = self.rect.copy()
        self.__maxvelocity = Vector2(config.PLAYER_MAX_SPEED, 100)
        self.__startspeed = 1.5

        self._velocity = Vector2()
        self._input = 0
        self._jumpforce = config.PLAYER_JUMPFORCE
        self._bonus_jumpforce = config.PLAYER_BONUS_JUMPFORCE

        self.gravity = config.GRAVITY
        self.accel = 0.5
        self.deccel = 0.6
        self.dead = False
        self.gyro_movement_modifier = 0.75 

    def init_gyro_sensor(self, retries=3):
        """
        Initialize the MPU6050 sensor with retry mechanism
        """
        try:
            from mpu6050 import mpu6050
            print(dir(mpu6050))
            for attempt in range(retries):
                try:
                    self.gyro_sensor = mpu6050.mpu6050(0x68)
                    # Verify the connection with a test read
                    test_data = self.gyro_sensor.get_temp()
                    self.gyro_threshold = 10  # Sensitivity threshold to detect tilt
                    print(f"Gyro sensor initialized successfully on attempt {attempt + 1}")
                    
                    # Configure the sensor with appropriate settings
                    # You might need to adjust these values based on your needs
                    self.gyro_sensor.set_gyro_range(self.gyro_sensor.GYRO_RANGE_250DEG)
                    self.gyro_sensor.set_accel_range(self.gyro_sensor.ACCEL_RANGE_2G)
                    return True
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(0.5)  # Wait before retry
                    
            raise Exception("Failed to initialize after all attempts")
                    
        except Exception as e:
            print(f"Warning: Could not initialize gyro sensor: {e}")
            print("Falling back to keyboard controls")
            self.gyro_sensor = None
            return False

    def read_gyro_input(self):
        """
        Reads the gyroscope data and sets the _input attribute for movement.
        Detects only the direction (left or right) and moves continuously in that direction.
        """
        if self.gyro_sensor is None:
            # Fallback to keyboard input if gyro is not available
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self._input = -1
                self._image = self._image_left
            elif keys[pygame.K_RIGHT]:
                self._input = 1
                self._image = self._image_right
            else:
                self._input = 0
            return

        try:
            # Read gyro data for x-axis rotation
            gyro_data = self.gyro_sensor.get_gyro_data()
            tilt_x = gyro_data['y']
            
            # Simple left/right detection
            if tilt_x > self.gyro_threshold:  # Tilted right
                self._input = -1
                self._image = self._image_left
            elif tilt_x < -self.gyro_threshold:  # Tilted left
                self._input = 1
                self._image = self._image_right
            else:
                # When gyro is stable (not tilted), stop movement
                self._input = 0

        except Exception as e:
            print(f"Warning: Could not read gyro data: {e}")
            # Try to reinitialize the sensor if there's an I2C error
            if "I2C" in str(e):
                print("Attempting to reinitialize sensor...")
                self.init_gyro_sensor()
            self._input = 0

    def fire_bullet(self):
        """
        Create a bullet and add it to the bullet group.
        """
        
        bullet_x = self.rect.centerx
        bullet_y = self.rect.top - 10
        new_bullet = Bullet(bullet_x, bullet_y, config.BULLET_SPEED, is_player_bullet=True)
        new_bullet.set_position(bullet_x, bullet_y)
        self.bullets.add(new_bullet)
        self._image = pygame.image.load("./images/penguin-shoot.png").convert_alpha()
        self._image = pygame.transform.scale(self._image, (40, 60))

    def _fix_velocity(self):
        """ Set player's velocity between max/min.
        Should be called in Player.update().
        """
        self._velocity.y = min(self._velocity.y, self.__maxvelocity.y)
        self._velocity.y = round(max(self._velocity.y, -self.__maxvelocity.y), 2)
        self._velocity.x = min(self._velocity.x, self.__maxvelocity.x)
        self._velocity.x = round(max(self._velocity.x, -self.__maxvelocity.x), 2)

    def reset(self):
        " Called only when game restarts (after player death)."
        self._velocity = Vector2()
        self.rect = self.__startrect.copy()
        self.camera_rect = self.__startrect.copy()
        self.dead = False
        self.bullets.empty()

    def handle_event(self, event: pygame.event.Event):
        current_time = time.time()
        if event.type == KEYDOWN and event.key == K_SPACE:
            self.button_pressed = True
            self.last_button_press_time = current_time
        elif event.type == pygame.KEYUP and event.key == K_SPACE:
            self.button_pressed = False

    def jump(self, force=None):
        if not force:
            force = self._jumpforce
        self._velocity.y = -force

    def onCollide(self, obj: Sprite):
        self.rect.bottom = obj.rect.top
        self.jump()

    def collisions(self):
        """ Checks for collisions with level.
        Should be called in Player.update().
        """
        lvl = Level.instance
        if not lvl:
            return
        for platform in lvl.platforms:
            # check falling and colliding <=> isGrounded ?
            if self._velocity.y > .5:
                # check collisions with platform's spring bonus
                if platform.bonus and collide_rect(self, platform.bonus):
                    self.onCollide(platform.bonus)
                    self.jump(platform.bonus.force)

                # check collisions with platform
                if collide_rect(self, platform):
                    self.onCollide(platform)
                    platform.onCollide()

    def update(self, camera: Camera):
        # Update player input based on gyro data or keyboard
        self.read_gyro_input()

        # Check if player out of screen: should be dead
        if self.rect.top > config.YWIN:
            self.dead = True

        # If player is dead, disable all actions
        if self.dead:
            self._velocity.x = 0
            self._velocity.y = 0
            return
            
        current_time = time.time()
        if (self.button_pressed or GPIO.input(BUTTON_GPIO_PIN) == GPIO.HIGH) and (current_time - self.last_button_press_time) >= self.button_press_delay and (current_time - self.last_fire_time) >= self.fire_cooldown:
            self.fire_bullet()
            self.last_fire_time = current_time
            self.last_button_press_time = current_time

        # Velocity update (apply gravity, input acceleration)
        self._velocity.y += self.gravity
        if self._input:  # Accelerate based on input
            if self.gyro_sensor:
                self._velocity.x += self._input * self.accel * self.gyro_movement_modifier
            else:
                self._velocity.x += self._input * self.accel
        elif self._velocity.x:  # Deccelerate
            if self.gyro_sensor:
                self._velocity.x -= getsign(self._velocity.x) * self.deccel * self.gyro_movement_modifier
            else:
                self._velocity.x -= getsign(self._velocity.x) * self.deccel
            self._velocity.x = round(self._velocity.x)
        self._fix_velocity()

        # Check for collisions with enemy bullets
        for enemy in Enemy.instances:
            for bullet in enemy.bullets:
                if pygame.sprite.collide_rect(self, bullet):
                    self._image = pygame.image.load("./images/tombstone.png").convert_alpha()
                    self._image = pygame.transform.scale(self._image, (60, 60))
                    bullet.kill()
                    self.dead = True
                    return

        # Position Update (prevent x-axis to be out of screen)
        self.rect.x = (self.rect.x + self._velocity.x) % (config.XWIN - self.rect.width)
        self.rect.y += self._velocity.y

        self.collisions()
        for bullet in self.bullets:
            bullet.update(camera)

    def draw(self, surface: pygame.Surface, camera: Camera):
        # Draw player with camera transformation
        surface.blit(self._image, camera.apply(self))
        
        # Draw each bullet with camera transformation
        for bullet in self.bullets:
            surface.blit(bullet._image, camera.apply(bullet))