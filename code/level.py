import pygame 
from support import import_csv_layout,import_tiles
from settings import tile_size, screen_height, screen_width
from tiles import  StaticTile, Money,AnimatedTile, EndBox
from player import Player
from particles import ParticleEffect
from game_data import levels

class Level:
    def __init__(self,current_level,surface,create_overworld,change_money,change_health):
        # general setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # audio 
        self.money_sound = pygame.mixer.Sound('../audio/coin.wav')
        # self.stomp_sound = pygame.mixer.Sound('../audio/effects/stomp.wav')

        # overworld connection 
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # player 
        player_layout = import_csv_layout(level_data['endbox'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout,change_health)

        # user interface 
        self.change_money = change_money

        #background image set up 
        self.background_image = pygame.image.load('../graphics/sprite/Background/Background.png')
        self.background_width = self.background_image.get_width()

        # dust 
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        #bgfloor
        bgfloor_layout=import_csv_layout(level_data['bgfloor'])
        self.bgfloor_sprites=self.create_tile_group(bgfloor_layout,'bgfloor')

        #floor
        floor_layout=import_csv_layout(level_data['floor'])
        self.floor_sprites=self.create_tile_group(floor_layout,'floor')
        
        #objects
        objects_layout=import_csv_layout(level_data['objects'])
        self.objects_sprites=self.create_tile_group(objects_layout,'objects')

        #ladder
        ladder_layout=import_csv_layout(level_data['ladder'])
        self.ladder_sprites=self.create_tile_group(ladder_layout,'ladder')

        #entry
        entry_layout=import_csv_layout(level_data['entry'])
        self.entry_sprites=self.create_tile_group(entry_layout,'entry')

        #hammer
        hammer_layout=import_csv_layout(level_data['hammer'])
        self.hammer_sprites=self.create_tile_group(hammer_layout,'hammer')

        # money 
        money_layout = import_csv_layout(level_data['money'])
        self.money_sprites = self.create_tile_group(money_layout,'money')

    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'bgfloor':
                        bgfloor_tile_dict = import_tiles('../graphics/sprite/bgfloor')
                        tile_path = bgfloor_tile_dict[f'{int(val)}.png']
                        sprite = StaticTile(tile_size,x,y,tile_path)
                        
                    if type == 'floor':
                        floor_tile_dict = import_tiles('../graphics/sprite/floor')
                        tile_path = floor_tile_dict[f'{int(val)}.png']
                        sprite = StaticTile(tile_size,x,y,tile_path)

                    if type == 'objects':
                        objects_tile_dict = import_tiles('../graphics/sprite/objects')
                        tile_path = objects_tile_dict[f'{int(val)}.png']
                        sprite = StaticTile(tile_size,x,y,tile_path)

                    if type == 'money':
                        sprite = Money(tile_size,x,y,'../graphics/sprite/money',5)

                    if type == 'entry' :
                        sprite = AnimatedTile(tile_size,x,y,'../graphics/sprite/entry')

                    if type == 'hammer' :
                        sprite = AnimatedTile(tile_size,x,y,'../graphics/sprite/hammer')

                    if type=='ladder':
                        if val=='0' : sprite = StaticTile(tile_size,x,y,'../graphics/sprite/ladder/0.png')
                        if val=='1' : sprite = StaticTile(tile_size,x,y,'../graphics/sprite/ladder/1.png')

                    sprite_group.add(sprite)
        
        return sprite_group

    def player_setup(self,layout, change_health):
        player_sprite = Player((0,256), self.display_surface,self.create_jump_particles, change_health)
        self.player.add(player_sprite)
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                # if val != '-1':
                #     sprite = EndBox(tile_size, x, y, val)
                #     self.goal.add(sprite)
                if val == '0':
                    sprite = StaticTile(tile_size,x,y,'../graphics/sprite/endbox/0.png')
                    self.goal.add(sprite)
                if val == '1':
                    sprite = StaticTile(tile_size,x,y,'../graphics/sprite/endbox/1.png')
                    self.goal.add(sprite)
                if val == '2':
                    sprite = StaticTile(tile_size,x,y,'../graphics/sprite/endbox/2.png')
                    self.goal.add(sprite)
                if val == '3':
                    sprite = StaticTile(tile_size,x,y,'../graphics/sprite/endbox/3.png')
                    self.goal.add(sprite)


    def create_jump_particles(self,pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else:
            pos += pygame.math.Vector2(10,-5)
        jump_particle_sprite = ParticleEffect(pos,'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed
        # collidable_sprites = self.entry_sprites.sprites() + self.hammer_sprites.sprites() + self.floor_sprites.sprites()
        collidable_sprites = self.floor_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0: 
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        # collidable_sprites = self.entry_sprites.sprites() + self.hammer_sprites.sprites()+ self.floor_sprites.sprites()
        collidable_sprites = self.floor_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0: 
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 3
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -3
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 3

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,'land')
            self.dust_sprite.add(fall_dust_particle)

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level,0)
            
    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
            self.create_overworld(self.current_level,self.new_max_level)
            
    def check_money_collisions(self):
        collided_money = pygame.sprite.spritecollide(self.player.sprite,self.money_sprites,True,pygame.sprite.collide_mask)
        if collided_money:
            self.money_sound.play()
            for money in collided_money:
                self.change_money(money.value)

    def check_entry_collisions(self):
        entry_collisions = pygame.sprite.spritecollide(self.player.sprite,self.entry_sprites,False,pygame.sprite.collide_mask)
        if entry_collisions:
            for sprite in entry_collisions:
                if not(sprite.frame_index >= 3 and sprite.frame_index <=5):
                    player = self.player.sprite
                    if player.direction.x < 0 and player.collision_rect.left+50>= sprite.rect.right: 
                        player.collision_rect.left = sprite.rect.right
                        player.on_left = True
                        self.current_x = player.rect.left
                    elif player.direction.x > 0 and player.collision_rect.right-50<= sprite.rect.left:
                        player.collision_rect.right = sprite.rect.left
                        player.on_right = True
                        self.current_x = player.rect.right
                    else:
                        self.player.sprite.get_damage()

    def check_hammer_collisions(self):
        hammer_collisions = pygame.sprite.spritecollide(self.player.sprite,self.hammer_sprites,False,pygame.sprite.collide_mask)
        if hammer_collisions:
            for sprite in hammer_collisions:
                if (sprite.frame_index >= 1 and sprite.frame_index <=6):
                    player = self.player.sprite
                    if player.direction.x < 0 and player.collision_rect.left+50>= sprite.rect.right: 
                        player.collision_rect.left = sprite.rect.right
                        player.on_left = True
                        self.current_x = player.rect.left
                    elif player.direction.x > 0 and player.collision_rect.right-50<= sprite.rect.left:
                        player.collision_rect.right = sprite.rect.left
                        player.on_right = True
                        self.current_x = player.rect.right
                    else:
                        self.player.sprite.get_damage()

    def check_ladder_collisions(self):
        player=self.player.sprite
        ladder_collisions=pygame.sprite.spritecollide(self.player.sprite,self.ladder_sprites,False,pygame.sprite.collide_mask)
        if ladder_collisions:
            player.status= 'ladder'
            # player.animations[player.status]
            player.direction.y = 0
            player.gravity = 0 
            # player.on_ground=False
            player.get_input()
        else:
            # player.on_ground=True
            player.gravity = 0.8
            player.get_status()
        # print(player.status)
                
    def run(self):
        # run the entire game / level
        for i in range(3):
            x_position = i * self.background_width
            self.display_surface.blit(self.background_image, (x_position, 0))

        #bgfloor
        self.bgfloor_sprites.update(self.world_shift)
        self.bgfloor_sprites.draw(self.display_surface)

        #floor
        self.floor_sprites.update(self.world_shift)
        self.floor_sprites.draw(self.display_surface)

        #objects
        self.objects_sprites.update(self.world_shift)
        self.objects_sprites.draw(self.display_surface)
        
        # dust particles 
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        #ladder
        self.ladder_sprites.update(self.world_shift)
        self.ladder_sprites.draw(self.display_surface)
        
        # hammer
        self.hammer_sprites.update(self.world_shift)
        self.hammer_sprites.draw(self.display_surface)

        # entry 
        self.entry_sprites.update(self.world_shift)
        self.entry_sprites.draw(self.display_surface)

        # money  
        self.money_sprites.update(self.world_shift)
        self.money_sprites.draw(self.display_surface)

        # player sprites
        self.player.update()
        self.horizontal_movement_collision()
        
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        
        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win()

        self.check_money_collisions()
        self.check_entry_collisions()
        self.check_hammer_collisions()
        self.check_ladder_collisions()
        

