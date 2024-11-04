from sprite import Sprite
import settings as config
import pygame
from bullet import Bullet  # Import Bullet class

class Enemy(Sprite):
    """
    A class to represent an enemy
    Inherits the Sprite class.
    """
    WIDTH = 15
    HEIGHT = 15
    SHOOT_INTERVAL = 1000  # Time in milliseconds between each shot

    def __init__(self, parent: Sprite, color=config.GRAY):
        self.parent = parent
        super().__init__(*self._get_initial_pos(), Enemy.WIDTH, Enemy.HEIGHT, color)
        self._image = pygame.image.load("./images/walrus.png").convert_alpha()
        self._image = pygame.transform.scale(self._image, (60, 40))

        self.last_shot_time = pygame.time.get_ticks()  # Time since last shot
        self.bullets = pygame.sprite.Group()  # Group to store enemy bullets

    def _get_initial_pos(self):
        x = self.parent.rect.centerx - Enemy.WIDTH // 2
        y = self.parent.rect.y - Enemy.HEIGHT - 20
        return x, y

    def shoot(self):
        """Make the enemy shoot a bullet downward."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= Enemy.SHOOT_INTERVAL:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, speed=-config.BULLET_SPEED)
            self.bullets.add(bullet)
            self.last_shot_time = current_time

    def update(self):
        """
        Update the enemy position and shoot bullets periodically.
        """
        if self.parent.slideable:
            self.rect.x = self.parent.rect.centerx - Enemy.WIDTH // 2
            self.rect.y = self.parent.rect.y - Enemy.HEIGHT - 15
        else:
            self._get_initial_pos()

        self.shoot()  # Call the shoot method to create bullets
        self.bullets.update()  # Update bullets

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the enemy and its bullets on the surface.
        """
        self.update()
        super().draw(surface)
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)
