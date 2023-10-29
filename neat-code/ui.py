import pygame

class UI:
	def __init__(self,surface):

		# setup 
		self.display_surface = surface 

		# health 
		self.health_bar = pygame.image.load('../graphics/sprite/health_bar/health_bar.png').convert_alpha()
		self.health_bar_topleft = (54,39)
		self.bar_max_width = 152
		self.bar_height = 4

		# money
		self.money = pygame.image.load('../graphics/sprite/money/0Money1.png').convert_alpha()
		self.money_rect = self.money.get_rect(topleft = (50,61))
		self.font = pygame.font.Font('../graphics/sprite/font/ARCADEPI.TTF',30)

	def show_health(self,current,full):
		self.display_surface.blit(self.health_bar,(20,10))
		current_health_ratio = current / full
		current_bar_width = self.bar_max_width * current_health_ratio
		health_bar_rect = pygame.Rect(self.health_bar_topleft,(current_bar_width,self.bar_height))
		pygame.draw.rect(self.display_surface,'#dc4949',health_bar_rect)

	def show_money(self,amount):
		self.display_surface.blit(self.money,self.money_rect)
		money_amount_surf = self.font.render(str(amount),False,'#33323d')
		money_amount_rect = money_amount_surf.get_rect(midleft = (self.money_rect.right + 4,self.money_rect.centery))
		self.display_surface.blit(money_amount_surf,money_amount_rect)


		