from sprite import Sprite
import settings as config
import pygame

class Enemy(Sprite):
    """
    A class to represent an enemy
    Inherits the Sprite class.
    """
    WIDTH = 15
    HEIGHT = 15

    def __init__(self, parent: Sprite, color=config.GRAY):
        self.parent = parent
        super().__init__(*self._get_initial_pos(), Enemy.WIDTH, Enemy.HEIGHT, color)
        self._image = pygame.image.load("./images/walrus.png").convert_alpha()
        self._image = pygame.transform.scale(self._image, (60, 40))

    def _get_initial_pos(self):
        x = self.parent.rect.centerx - Enemy.WIDTH // 2
        y = self.parent.rect.y - Enemy.HEIGHT - 20
        return x, y

    def update(self):
        """
        Update the enemy position to match the parent platform.
        """
        if self.parent.slideable:
            self.rect.x = self.parent.rect.centerx - Enemy.WIDTH//2
            self.rect.y = self.parent.rect.y - Enemy.HEIGHT - 15
        else:
            self._get_initial_pos()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the enemy on the surface.
        """
        self.update()
        super().draw(surface)