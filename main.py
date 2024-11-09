import pygame, sys
from singleton import Singleton
from camera import Camera
from player import Player
from level import Level
import settings as config
from enemy import Enemy

class Game(Singleton):
	"""
	A class to represent the game.

	used to manage game updates, draw calls and user input events.
	Can be access via Singleton: Game.instance .
	(Check Singleton design pattern for more info)
	"""

	# constructor called on new instance: Game()
	def __init__(self) -> None:
		
		# ============= Initialisation =============
		self.__alive = True
		# Window / Render
		self.window = pygame.display.set_mode(config.DISPLAY,config.FLAGS)
		self.clock = pygame.time.Clock()

		self.background = pygame.image.load("./images/background.png").convert()
		self.background = pygame.transform.scale(self.background, config.DISPLAY)

		# Instances
		self.camera = Camera()
		self.lvl = Level()
		self.player = Player(
			config.HALF_XWIN - config.PLAYER_SIZE[0]/2,# X POS
			config.HALF_YWIN + config.HALF_YWIN/2,#      Y POS
			*config.PLAYER_SIZE,# SIZE
			config.PLAYER_COLOR#  COLOR
		)

		self.bullets = pygame.sprite.Group()


		# User Interface
		self.score = 0
		self.score_txt = config.SMALL_FONT.render("0 m",1,config.GRAY)
		self.score_pos = pygame.math.Vector2(10,10)

		# Game over text and restart instruction text
		self.gameover_txt = config.LARGE_FONT.render("Game Over", 1, config.WHITE)
		self.restart_txt = config.SMALL_FONT.render("Press Spacebar to restart the game", 1, config.WHITE)

		# Center the game over text and place the restart text slightly below
		self.gameover_rect = self.gameover_txt.get_rect(center=(config.HALF_XWIN, config.HALF_YWIN - 30))
		self.restart_rect = self.restart_txt.get_rect(center=(config.HALF_XWIN, config.HALF_YWIN + 30))
				
				
	def close(self):
		self.__alive = False


	def reset(self):
		self.camera.reset()
		self.lvl.reset()
		self.player.reset()

		# Reset the enemies and their bullets
		for enemy in Enemy.instances:
			enemy.reset()

	def _event_loop(self):
		# ---------- User Events ----------
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.close()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.close()
				if event.key == pygame.K_SPACE and self.player.dead:
					self.reset()
			self.player.handle_event(event)


	def _update_loop(self):
		# ----------- Update -----------
		self.player.update(self.camera)
		self.lvl.update()

		if not self.player.dead:
			self.camera.update(self.player.rect)
			#calculate score and update UI txt
			self.score=-self.camera.state.y//50
			self.score_txt = config.SMALL_FONT.render(
				str(self.score)+" m", 1, config.GRAY)
	

	def _render_loop(self, camera: Camera):
		# ----------- Display -----------
		#self.window.fill(config.WHITE)
		self.window.blit(self.background, (0,0))
		self.lvl.draw(self.window, camera)
		self.player.draw(self.window, Camera.instance)

		# User Interface
		if self.player.dead:
			self.window.blit(self.gameover_txt,self.gameover_rect)# gameover txt
			self.window.blit(self.restart_txt, self.restart_rect)
		self.window.blit(self.score_txt, self.score_pos)# score txt

		pygame.display.update()# window update
		self.clock.tick(config.FPS)# max loop/s


	def run(self):
		# ============= MAIN GAME LOOP =============
		while self.__alive:
			self._event_loop() 
			self._update_loop()
			self._render_loop(self.camera)
		pygame.quit()

if __name__ == "__main__":
	# ============= PROGRAM STARTS HERE =============
	game = Game()
	game.run()