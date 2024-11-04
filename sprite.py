import pygame
from pygame import Surface, Rect
from camera import Camera

class Sprite(pygame.sprite.Sprite):  # Inherit from pygame.sprite.Sprite
    """
    A class to represent a sprite.

    Used for pygame displaying.
    Image generated with given color and size.
    """
    def __init__(self, x: int, y: int, w: int, h: int, color: tuple):
        super().__init__()  # Initialize pygame.sprite.Sprite
        self.__color = color
        self._image = Surface((w, h))
        self._image.fill(self.color)
        self._image = self._image.convert()
        self.rect = Rect(x, y, w, h)
        self.camera_rect = self.rect.copy()

    @property
    def image(self) -> Surface:
        return self._image

    @property
    def color(self) -> tuple:
        return self.__color

    @color.setter
    def color(self, new: tuple) -> None:
        assert isinstance(new, tuple) and len(new) == 3, "Value is not a color"
        self.__color = new
        self._image.fill(self.color)

    def draw(self, surface: Surface) -> None:
        """
        Render method, should be called every frame after update.
        :param surface pygame.Surface: the surface to draw on.
        """
        if Camera.instance:
            self.camera_rect = Camera.instance.apply(self)
            surface.blit(self._image, self.camera_rect)
        else:
            surface.blit(self._image, self.rect)
