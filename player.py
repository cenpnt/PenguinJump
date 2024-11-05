from math import copysign
import pygame
from pygame.math import Vector2
from pygame.locals import KEYDOWN,KEYUP,K_LEFT,K_RIGHT, K_SPACE
from pygame.sprite import collide_rect
from pygame.event import Event
from camera import Camera
from singleton import Singleton
from sprite import Sprite
from level import Level
from bullet import Bullet
import settings as config
from enemy import Enemy

#Return the sign of a number: getsign(-5)-> -1
getsign = lambda x : copysign(1, x)

class Player(Sprite, Singleton):
	"""
	A class to represent the player.
	Manages player's input, physics (movement...).
	Can be access via Singleton: Player.instance.
	(Check Singleton design pattern for more info).
	"""
	# (Overriding Sprite.__init__ constructor)
	def __init__(self, *args):
		# calling default Sprite constructor
		Sprite.__init__(self, *args)
		# Create image attribute directly on the instance
		self._image = pygame.image.load("./images/penguin-right.png").convert_alpha()
		self._image = pygame.transform.scale(self._image, (60, 60))
		self.bullets = pygame.sprite.Group()  # Group to store bullets

		# Set rect based on the image dimensions
		self._rect = self._image.get_rect()
		self.__startrect = self.rect.copy()
		self.__maxvelocity = Vector2(config.PLAYER_MAX_SPEED, 100)
		self.__startspeed = 1.5

		self._velocity = Vector2()
		self._input = 0
		self._jumpforce = config.PLAYER_JUMPFORCE
		self._bonus_jumpforce = config.PLAYER_BONUS_JUMPFORCE

		self.gravity = config.GRAVITY
		self.accel = .5
		self.deccel = .6
		self.dead = False

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


	def _fix_velocity(self) -> None:
		""" Set player's velocity between max/min.
		Should be called in Player.update().
		"""
		self._velocity.y = min(self._velocity.y, self.__maxvelocity.y)
		self._velocity.y = round(max(self._velocity.y, -self.__maxvelocity.y), 2)
		self._velocity.x = min(self._velocity.x, self.__maxvelocity.x)
		self._velocity.x = round(max(self._velocity.x, -self.__maxvelocity.x), 2)

	def reset(self) -> None:
		" Called only when game restarts (after player death)."
		self._velocity = Vector2()
		self.rect = self.__startrect.copy()
		self.camera_rect = self.__startrect.copy()
		self.dead = False
		self.bullets.empty()

	def handle_event(self, event: Event) -> None:
		""" Called in main loop foreach user input event.
		:param event pygame.Event: user input event
		"""
		# Check if start moving
		if event.type == KEYDOWN:
			# Moves player only on x-axis (left/right)
			if event.key == K_LEFT:
				self._velocity.x = -self.__startspeed
				self._input = -1
				self._image = pygame.image.load("./images/penguin-left.png").convert_alpha()
				self._image = pygame.transform.scale(self._image, (60, 60))
			elif event.key == K_RIGHT:
				self._velocity.x = self.__startspeed
				self._input = 1
				self._image = pygame.image.load("./images/penguin-right.png").convert_alpha()
				self._image = pygame.transform.scale(self._image, (60, 60))
			elif event.key == K_SPACE:
				self.fire_bullet()
		# Check if stop moving
		elif event.type == KEYUP:
			if (event.key == K_LEFT and self._input == -1) or (event.key == K_RIGHT and self._input == 1):
				self._input = 0

	def jump(self, force: float = None) -> None:
		if not force: force = self._jumpforce
		self._velocity.y = -force

	def onCollide(self, obj: Sprite) -> None:
		self.rect.bottom = obj.rect.top
		self.jump()

	def collisions(self) -> None:
		""" Checks for collisions with level.
		Should be called in Player.update().
		"""
		lvl = Level.instance
		if not lvl: return
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

	def update(self, camera: Camera) -> None:
		# Check if player out of screen: should be dead
		if self.rect.top > config.YWIN:
			self.dead = True

		# If player is dead, disable all actions
		if self.dead:
			self._velocity.x = 0
			self._velocity.y = 0
			return

		# Velocity update (apply gravity, input acceleration)
		self._velocity.y += self.gravity
		if self._input:  # accelerate
			self._velocity.x += self._input * self.accel
		elif self._velocity.x:  # deccelerate
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

	def draw(self, surface: pygame.Surface, camera: Camera) -> None:
		# Draw player with camera transformation
		surface.blit(self._image, camera.apply(self))
		
		# Draw each bullet with camera transformation
		for bullet in self.bullets:
			surface.blit(bullet._image, camera.apply(bullet))

	