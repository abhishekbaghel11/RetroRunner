import pygame, sys 
import neat 
from settings import * 
from overworld import Overworld
from level import Level
from ui import UI
import math 
import os 
import pickle 

#create some global variables
player_coor = None 
goal_coor = None
distance = None
run_2 = None
run = None

player_initial_pos_x = 0

class Game:
    def __init__(self, screen):
        self.max_level = 0
        self.money = 0
        self.max_health = 100		
        self.cur_health = 100
        self.fitness = 0 
        self.screen = screen

        # audio 
        self.level_bg_music = pygame.mixer.Sound('../audio/main.ogg')
        self.overworld_bg_music = pygame.mixer.Sound('../audio/main.ogg')
        self.overworld_bg_music.set_volume(0.3)

        self.level = Level(0, self.screen, self.change_money, self.change_health)

        self.ui= UI(self.screen) 

        self.count = 0 

    # def create_level(self,current_level):
    #     self.level = Level(current_level, screen, self.create_overworld,self.change_money,self.change_health)
    #     self.status = 'level'
    #     self.money=0
    #     self.cur_health=self.max_health
    #     self.overworld_bg_music.stop()
    #     self.level_bg_music.play(loops = -1)

    # def create_overworld(self, current_level, new_max_level):
    #     if new_max_level > self.max_level:
    #         self.max_level = new_max_level
    #     self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
    #     self.status = 'overworld'		
    #     self.overworld_bg_music.play(loops = -1)
    #     self.level_bg_music.stop()

    def change_money(self,amount):
        self.money+=amount
        self.fitness += 10 
    
    def change_health(self,amount):
        self.cur_health+=amount
        self.fitness -= 5

    def check_game_over(self):
        # if self.cur_health <= 0:
        #     self.cur_health = 100
        #     self.money = 0
        #     self.max_level = 0
        #     self.overworld = Overworld(0,self.max_level,screen,self.create_level)
        #     self.status = 'overworld'
        #     self.level_bg_music.stop()
        #     self.overworld_bg_music.play(loops = -1)
        global run
        if self.cur_health <= 0 or self.count == 600:
            self.fitness -= 100
            run = False
        

    def fitness_distance(self):
        global player_coor, goal_coor,player_initial_pos_x, distance

        if player_initial_pos_x < self.level.player.sprite.rect.x:
            self.fitness += 2000/(distance+1)           
        else:
            self.fitness -= 500/(distance+1)

        if abs(player_initial_pos_x - self.level.player.sprite.rect.x) <= 1:
            self.count += 1
        else:
            self.count = 0


    def run(self):
        # if self.status == 'overworld':
        #     self.overworld.run()
        # else:
        #     self.level.run()
        #     self.ui.show_health(self.cur_health,self.max_health)
        #     self.ui.show_money(self.money)
        #     self.check_game_over()
        global run_2, player_coor, goal_coor, distance
        
        self.level.run()
        level_fitness, run_2, player_coor, goal_coor = self.level.update_var()
        distance = math.sqrt((player_coor[0] - goal_coor[0])**2 + (player_coor[1] - goal_coor[1])**2)
        self.fitness += level_fitness
        self.ui.show_health(self.cur_health,self.max_health)
        self.ui.show_money(self.money)
        self.check_game_over()
        self.fitness_distance()
    
    def update_fitness(self):
        return self.fitness
    

def main(genomes, config): #the genomes are the entities present in a generation 
    global distance, player_coor, goal_coor, run, run_2, player_initial_pos_x

    nets = [] #list of neural networks for each genome(player) for a single gen
    ge = [] #list of genomes for a single gen 
    games = [] #list of games(in which each player runs)

    genome_counter = 0 

    for _, g in genomes:
        genome_counter += 1
        pygame.init()
        screen = pygame.display.set_mode((screen_width,screen_height))
        clock = pygame.time.Clock()

        ####Create custom key events 
        # key_event_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        # key_event_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        # key_event_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        
        player_coor = None 
        goal_coor = None
        distance = None
        run_2 = True
        run = True 
        player_intial_pos_x = 0 

        penalty = None

        net = neat.nn.FeedForwardNetwork.create(g, config) #create the neural network for the genome 
        nets.append(net) #append the nn in the nets 
        game = Game(screen)
        games.append(game)
        g.fitness = 0 #initialize the fitness function 
        ge.append(g) #append the genome in the list of genomes

        while run and run_2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    penalty_time = pygame.time.get_ticks()
                    if penalty_time < 3000:
                        penalty = 1
                    elif penalty_time < 10000 and penalty_time >= 3000:
                        penalty = 2
                    elif penalty_time < 20000 and penalty_time >= 10000:
                        penalty = 3
                    else:
                        penalty = 4
                    run = False
        
            # print(pygame.time.get_ticks()) -----------------------------------------------------------------

            screen.fill('#165145')
            game.run()
            g.fitness = game.update_fitness()

            output = net.activate((player_coor[0], player_coor[1], goal_coor[0], goal_coor[1],abs(player_coor[0]-goal_coor[0]),distance,int(game.level.player.sprite.on_ground),int(game.level.player.sprite.facing_right)))
           
            decision = output.index(max(output))
        
            if decision == 0 and game.level.player.sprite.on_ground:
                # pygame.event.post(key_event_space)
                game.level.player.sprite.jump()
                game.level.player.sprite.create_jump_particles(game.level.player.sprite.rect.midbottom)
            elif decision == 1:
                # pygame.event.post(key_event_left)
                game.level.player.sprite.direction.x = -1
                game.level.horizontal_movement_collision(4)
                game.level.scroll_x()
                game.level.player.sprite.facing_right = False
            elif decision == 2:
                # pygame.event.post(key_event_right)
                game.level.player.sprite.direction.x = 1
                game.level.horizontal_movement_collision(4)
                game.level.scroll_x()
                game.level.player.sprite.facing_right = True
            elif decision == 3 and game.level.player.sprite.status == 'ladder':
                game.level.player.sprite.direction.y = -2
            elif decision == 4 and game.level.player.sprite.status == 'ladder':
                game.level.player.sprite.direction.y = 2

            #update the player_initial_pos_per_frame
            player_initial_pos_x = game.level.player.sprite.rect.x   
            pygame.display.update()
            clock.tick(60)
        
        if penalty == 1:
            g.fitness -= 300
        elif penalty == 2:
            g.fitness -= 100
        elif penalty == 3:
            g.fitness -= 50
        elif penalty == 4:
            g.fitness -= 10
        else:
            pass
        pygame.quit()
        # print(g.fitness) #-----------------------------------------------------------------------------

        # time.sleep(5) #-----------------------------------------------------------------------------

#function to run the neat algo 
def run(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-27')
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(main, 50) #run upto 50 generations

    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)
        
if __name__ == "__main__":
    # local_dir = os.path.dirname(__file__)


    
    local_dir = os.getcwd()
    config_path = os.path.join(local_dir, "config_neat.txt")
    run(config_path)     
