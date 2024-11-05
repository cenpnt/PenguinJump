from random import randint
from pygame import Surface
import pygame
import asyncio
from singleton import Singleton
from sprite import Sprite
import settings as config
from random import choice
from enemy import Enemy
from camera import Camera

#return True with a chance of: P(X=True)=1/x
chance = lambda x: not randint(0,x)

class Bonus(Sprite):
	"""
	A class to represent a bonus
	Inherits the Sprite class.
	"""

	WIDTH = 15
	HEIGHT = 15

	def __init__(self, parent:Sprite,color=config.GRAY, force=config.PLAYER_BONUS_JUMPFORCE):

		self.parent = parent
		super().__init__(*self._get_inital_pos(), Bonus.WIDTH, Bonus.HEIGHT, color)
		self.force = force
		self._image = pygame.image.load("./images/fish.png").convert_alpha()
		self._image = pygame.transform.scale(self._image, (50, 30))

	def _get_inital_pos(self):
		x = self.parent.rect.centerx - Bonus.WIDTH//2
		y = self.parent.rect.y - Bonus.HEIGHT - 20
		return x,y

	def update(self):
		"""
		Update the bonus position to match the parent platform.
		"""
		if self.parent.slideable:
			self.rect.x = self.parent.rect.centerx - Bonus.WIDTH//2
			self.rect.y = self.parent.rect.y - Bonus.HEIGHT - 15
		else:
			self._get_inital_pos()

	def draw(self, surface:Surface) -> None:
		"""
		Draw the bonus on the surface.
		"""
		self.update()
		super().draw(surface)


class Platform(Sprite):
	"""
	A class to represent a platform.

	Should only be instantiated by a Level instance.
	Can have a bonus spring or broke on player jump.
	Inherits the Sprite class.
	"""
	# (Overriding inherited constructor: Sprite.__init__)
	def __init__(self, x:int, y:int, width:int, height:int, initial_bonus=False, breakable=False, slideable=False, has_enemy=False):
		color = config.PLATFORM_COLOR
		if breakable:color = config.PLATFORM_COLOR_LIGHT
		super().__init__(x,y,width,height,color)

		self.slideable = slideable
		self.breakable = breakable
		self.__level = Level.instance
		self.__bonus = None
		self.__enemy = None
		if has_enemy:
			self.add_enemy(Enemy)

		if initial_bonus:
			self.add_bonus(Bonus)

		self.speed = config.PLATFORM_SPEED if self.slideable else 0
		self.direction = choice([-1,1]) if self.slideable else 0
		self._image = pygame.image.load("./images/platform.png").convert_alpha()
		self._image = pygame.transform.scale(self._image, (120, 30))

	# Public getter for __bonus so it remains private
	@property
	def bonus(self):return self.__bonus

	@property
	def enemy(self):return self.__enemy

	def add_bonus(self,bonus_type:type) -> None:
		""" Safely adds a bonus to the platform.
		:param bonus_type type: the type of bonus to add.
		"""
		assert issubclass(bonus_type,Bonus), "Not a valid bonus type !"
		if not self.__bonus and not self.breakable and not self.__enemy:
			self.__bonus = bonus_type(self)

	def add_enemy(self, enemy_type: type) -> None:
		"""
		Safely adds an enemy to the platform.
		:param enemy_type type: the type of enemy to add.
		"""
		assert issubclass(enemy_type, Enemy), "Not a valid enemy type!"
		if not self.__enemy and not self.breakable and not self.__bonus:
			self.__enemy = enemy_type(self)

	def remove_bonus(self) -> None:
		" Safely removes platform's bonus."
		self.__bonus = None

	def remove_enemy(self) -> None:
		"""Safely removes platform's enemy."""
		self.__enemy = None

	def onCollide(self) -> None:
		" Called in update if collision with player (safe to overrided)."
		if self.breakable:
			self.__level.remove_platform(self)

	# ( Overriding inheritance: Sprite.draw() )
	def draw(self, surface:Surface, camera: Camera) -> None:
		""" Like Sprite.draw().
		Also draws the platform's bonus if it has one.
		:param surface pygame.Surface: the surface to draw on.
		"""
		# check if out of screen: should be deleted
		self.slide()
		super().draw(surface)
		if self.__bonus:
			self.__bonus.draw(surface)
		if self.__enemy:
			self.__enemy.draw(surface, camera)
		if self.camera_rect.y+self.rect.height>config.YWIN:
			self.__level.remove_platform(self)
		if self.breakable:
			self._image = pygame.image.load("./images/ice_break.png").convert_alpha()
			self._image = pygame.transform.scale(self._image, (120, 30))

	def slide(self):
		if self.slideable:
			self.rect.x += self.speed * self.direction
			if self.rect.right >= config.XWIN or self.rect.left <= 0:
				self.direction *= -1
			

class Level(Singleton):
	"""
	A class to represent the level.
	
	used to manage updates/generation of platforms.
	Can be access via Singleton: Level.instance.
	(Check Singleton design pattern for more info)
	"""
	
	# constructor called on new instance: Level()
	def __init__(self):
		self.platform_size = config.PLATFORM_SIZE
		self.max_platforms = config.MAX_PLATFORM_NUMBER
		self.distance_min = min(config.PLATFORM_DISTANCE_GAP)
		self.distance_max = max(config.PLATFORM_DISTANCE_GAP)

		self.bonus_platform_chance = config.BONUS_SPAWN_CHANCE
		self.breakable_platform_chance = config.BREAKABLE_PLATFORM_CHANCE
		self.slideable_platform_chance = config.SLIDEABLE_PLATFORM_CHANCE
		self.enemy_spawn_chance = config.ENEMY_SPAWN_CHANCE

		self.__platforms = []
		self.__to_remove = []

		self.__base_platform = Platform(
			config.HALF_XWIN - self.platform_size[0]//2,# X POS
			config.HALF_YWIN + config.YWIN/3, #           Y POS
			*self.platform_size)#                         SIZE
	

	# Public getter for __platforms so it remains private
	@property
	def platforms(self) -> list:
		return self.__platforms


	async def _generation(self) -> None:
		" Asynchronous management of platforms generation."
		# Check how many platform we need to generate
		nb_to_generate = self.max_platforms - len(self.__platforms)
		for _ in range(nb_to_generate):
			self.create_platform()	


	def create_platform(self) -> None:
		" Create the first platform or a new one."
		if self.__platforms:
			# Generate a new random platform :
			# x position along screen width
			# y position starting from last platform y pos +random offset
			offset = randint(self.distance_min,self.distance_max)
			self.__platforms.append(Platform(
				randint(0,config.XWIN-self.platform_size[0]),#       X POS
				self.__platforms[-1].rect.y-offset,#                 Y POS
				*self.platform_size, #                               SIZE
				initial_bonus=chance(self.bonus_platform_chance),# HAS A Bonus
				breakable=chance(self.breakable_platform_chance),#  IS BREAKABLE
				slideable=chance(self.slideable_platform_chance),# IS SLIDEABLE
				has_enemy=chance(self.enemy_spawn_chance) # HAS AN ENEMY
				))
				
		else:
			# (just in case) no platform: add the base one
			self.__platforms.append(self.__base_platform)


	def remove_platform(self,plt:Platform) -> bool:
		""" Removes a platform safely.
		:param plt Platform: the platform to remove
		:return bool: returns true if platoform successfully removed
		"""
		if plt in self.__platforms:
			self.__to_remove.append(plt)
			return True
		return False


	def reset(self) -> None:
		" Called only when game restarts (after player death)."
		self.__platforms = [self.__base_platform]

	def update(self) -> None:
		"""Called each frame in main game loop for generation."""
		for platform in self.__to_remove:
			if platform in self.__platforms:
				self.__platforms.remove(platform)
		self.__to_remove = []
		asyncio.run(self._generation())


	def draw(self,surface:Surface, camera: Camera) -> None:
		""" Called each frame in main loop, draws each platform
		:param surface pygame.Surface: the surface to draw on.
		"""
		for platform in self.__platforms:
			platform.draw(surface, camera)