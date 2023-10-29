import pygame, sys 
from settings import * 
from overworld import Overworld
from level import Level
from ui import UI

class Game:
    def __init__(self):
        self.max_level = 0
        self.money=0
        self.max_health = 100		
        self.cur_health = 100
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        self.ui= UI(screen)
        # audio 
        self.level_bg_music = pygame.mixer.Sound('../audio/main.ogg')
        self.overworld_bg_music = pygame.mixer.Sound('../audio/overworld_music.wav')
        self.overworld_bg_music.play(loops = -1)
        self.overworld_bg_music.set_volume(0.3)

    def create_level(self,current_level):
        self.level = Level(current_level, screen, self.create_overworld,self.change_money,self.change_health)
        self.status = 'level'
        self.money=0
        self.cur_health=self.max_health
        self.overworld_bg_music.stop()
        self.level_bg_music.play(loops = -1)

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'		
        self.overworld_bg_music.play(loops = -1)
        self.level_bg_music.stop()

    def change_money(self,amount):
        self.money+=amount
    
    def change_health(self,amount):
        self.cur_health+=amount

    def check_game_over(self):
        if self.cur_health <= 0:
            self.cur_health = 100
            self.money = 0
            self.max_level = 0
            self.overworld = Overworld(0,self.max_level,screen,self.create_level)
            self.status = 'overworld'
            self.level_bg_music.stop()
            self.overworld_bg_music.play(loops = -1)

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.cur_health,self.max_health)
            self.ui.show_money(self.money)
            self.check_game_over()

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Retro Runnner')
clock = pygame.time.Clock()
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('#165145')
    game.run()

    pygame.display.update()
    clock.tick(60)