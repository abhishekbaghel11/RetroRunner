
import pygame
from support import import_folder

class Tile(pygame.sprite.Sprite):
	def __init__(self,size,x,y):
		super().__init__()
		self.image = pygame.Surface((size,size))
		self.rect = self.image.get_rect(topleft = (x,y))

	def update(self,shift):
		self.rect.x += shift

class StaticTile(Tile):
	def __init__(self,size,x,y,path): #surface --> image
		super().__init__(size,x,y)
		self.image = pygame.image.load(path).convert_alpha()
		offset_y = y + size
		self.rect = self.image.get_rect(bottomleft = (x,offset_y))

class EndBox(Tile):
	def __init__(self,size,x,y,val):
		super().__init__(size,x,y)
		self.image = pygame.image.load(f"../graphics/sprite/endbox/{val}.png").convert_alpha()
		offset_y = y + size 
		self.rect = self.image.get_rect(bottomleft = (x,offset_y))

class AnimatedTile(Tile):
	def __init__(self,size,x,y,path):
		super().__init__(size,x,y)
		self.frames = import_folder(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]

		offset_y = y + size #size only 32 --> half the size of height for entry and exit
		self.rect = self.image.get_rect(bottomleft = (x,offset_y))

	def animate(self):
		self.frame_index += 0.10
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self,shift):
		self.animate()
		self.rect.x += shift

class Money(AnimatedTile):
	def __init__(self,size,x,y,path,value):
		super().__init__(size,x,y,path)
		center_x = x + int(size / 2)
		center_y = y + int(size / 2)
		self.rect = self.image.get_rect(center = (center_x,center_y))
		self.value = value

#for objects use offset_y --> y + size(32)


