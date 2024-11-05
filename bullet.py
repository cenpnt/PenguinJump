import pygame
from sprite import Sprite
import settings as config
from math import copysign
from camera import Camera

# Return the sign of a number: getsign(-5) -> -1
getsign = lambda x: copysign(1, x)

class Bullet(Sprite):
    """
    A class to represent a bullet.
    Inherits the Sprite class.
    """
    WIDTH = 5
    HEIGHT = 15

    def __init__(self, x: int, y: int, speed: int = config.BULLET_SPEED, color=config.BULLET_COLOR, is_player_bullet: bool = True):
        """
        Initialize the bullet with a position, speed, color, and type.
        :param is_player_bullet: If True, bullet was fired by player; else by enemy.
        """
        super().__init__(x, y, Bullet.WIDTH, Bullet.HEIGHT, color)
        self.speed = speed
        self.is_player_bullet = is_player_bullet
        self._image = pygame.Surface((Bullet.WIDTH, Bullet.HEIGHT))
        self._image.fill(color)

    def update(self, camera: Camera):
        # Move bullet upwards or downwards based on its type
        self.rect.y -= self.speed if self.is_player_bullet else -self.speed
        
        # Remove bullet if it goes out of screen bounds
        if self.rect.bottom < camera.state.top or self.rect.top > camera.state.bottom:
            self.kill()

    def set_position(self, penguin_x: int, penguin_y: int):
        """
        Set the bullet's position to match the penguin's current position.
        This method is called when firing the bullet.
        """
        self.rect.x = penguin_x
        self.rect.y = penguin_y

 


    
    