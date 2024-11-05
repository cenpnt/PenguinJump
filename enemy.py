from __future__ import annotations
from typing import TYPE_CHECKING
from sprite import Sprite
import settings as config
import pygame
from bullet import Bullet
from camera import Camera

if TYPE_CHECKING:
    from player import Player

class Enemy(Sprite):
    """
    A class to represent an enemy
    Inherits the Sprite class.
    """
    WIDTH = 50
    HEIGHT = 15
    SHOOT_INTERVAL = 1000  # Time in milliseconds between each shot

    instances = []

    def __init__(self, parent: Sprite, color=config.GRAY):
        self.parent = parent
        super().__init__(*self._get_initial_pos(), Enemy.WIDTH, Enemy.HEIGHT, color)
        self._image = pygame.image.load("./images/walrus.png").convert_alpha()
        self._image = pygame.transform.scale(self._image, (60, 40))
        self.last_shot_time = pygame.time.get_ticks()  # Time since last shot
        self.bullets = pygame.sprite.Group()  # Group to store enemy bullets

        Enemy.instances.append(self)

    def _get_initial_pos(self):
        x = self.parent.rect.centerx - Enemy.WIDTH // 2
        y = self.parent.rect.y - Enemy.HEIGHT - 20
        return x, y

    def handle_bullet_collision(self, bullet: Bullet):
        """Handle collision between enemy and a bullet."""
        # Check if the bullet belongs to the player
        from player import Player
        if bullet in Player.instance.bullets:
            self.kill()  # Remove the enemy from the game

    def check_player_bullet_collision(self):
        """Check for collisions with player bullets."""
        from player import Player
        for bullet in Player.instance.bullets:
            if self.rect.colliderect(bullet.rect):
                self.handle_bullet_collision(bullet)

    def shoot(self):
        """Make the enemy shoot a bullet downward."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= Enemy.SHOOT_INTERVAL:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, speed=-config.BULLET_SPEED)
            self.bullets.add(bullet)
            self.last_shot_time = current_time

    def update(self, camera: Camera):
        """Update the enemy position and shoot bullets periodically."""
        if self in Enemy.instances:
            if self.parent.slideable:
                self.rect.x = self.parent.rect.centerx - Enemy.WIDTH // 2
                self.rect.y = self.parent.rect.y - Enemy.HEIGHT - 15
            else:
                self._get_initial_pos()
            self.shoot()  # Call the shoot method to create bullets
            self.bullets.update(camera)  # Update bullets
            self.check_player_bullet_collision()

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the enemy and its bullets on the surface."""
        if self in Enemy.instances:
            self.update(camera)
            super().draw(surface)
            # Draw bullets
            for bullet in self.bullets:
                bullet.draw(surface)

    def kill(self):
        """Remove the enemy from the game."""
        super().kill()
        if self in Enemy.instances:
            print("killed by player")
            Enemy.instances.remove(self)
            self.bullets.empty()  # Remove all bullets

    def reset(self):
        self.bullets.empty()
        self.last_shot_time = pygame.time.get_ticks()
        if self in Enemy.instances:
            Enemy.instances.remove(self)