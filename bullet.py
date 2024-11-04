import pygame
from sprite import Sprite
import settings as config
from math import copysign

# Return the sign of a number: getsign(-5) -> -1
getsign = lambda x: copysign(1, x)

class Bullet(Sprite):
    """
    A class to represent a bullet.
    Inherits the Sprite class.
    """
    WIDTH = 5
    HEIGHT = 15

    def __init__(self, x: int, y: int, speed: int = config.BULLET_SPEED, color=config.BULLET_COLOR):
        """
        Initialize the bullet with a position, speed, and color.
        :param x: The initial x-coordinate of the bullet.
        :param y: The initial y-coordinate of the bullet.
        :param speed: The speed at which the bullet travels.
        :param color: The color of the bullet.
        """
        super().__init__(x, y, Bullet.WIDTH, Bullet.HEIGHT, color)
        self.speed = speed
        self._image = pygame.Surface((Bullet.WIDTH, Bullet.HEIGHT))
        self._image.fill(color)

    def update(self):
        """
        Update the bullet's position by moving it upwards.
        """
        self.rect.y -= self.speed
        # Optionally, remove bullet if it goes out of screen bounds
        if self.rect.bottom < 0:
            self.kill()  # Removes bullet from all groups it's in

    def set_position(self, penguin_x: int, penguin_y: int):
        """
        Set the bullet's position to match the penguin's current position.
        This method is called when firing the bullet.
        """
        self.rect.x = penguin_x
        self.rect.y = penguin_y