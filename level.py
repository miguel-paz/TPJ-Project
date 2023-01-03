import pygame
import random 
import numpy as np
import copy

from settings import *
from player import Player
from enemy import Enemy
from coin import Coin
from gui import GUI
from particles import ParticleEffect
from sprites import PlayerSprite, TileSprite, StaticTileSprite, CrateSprite, CoinSprite, PalmSprite, EnemySprite, GUISprite, WinLoseSprite
from support import import_csv, import_cut_tiles


class Level:
    def __init__(self, level_data, level_type, surface):
        self.level_data = level_data
        self.level_type = level_type
        self.display_surface = surface
        
        self.win = None
        self.player = None
        self.player_init_pos = None
        self.level_coins = 0
        self.gui = None
        self.world_shift = 0
        self.world_shifted = 0
        self.survival_shift = -1
        self.current_x = 0
        self.fall_damage = 1/4
        self.built = False
        self.start_time = 0
        self.current_time = 0
        
        #dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        #self.player_on_ground = False
        
        self.end_screen = pygame.sprite.GroupSingle()
        
        self.tiles = pygame.sprite.Group()
        self.decoration_tiles = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.GroupSingle()
        self.gui_sprite = pygame.sprite.GroupSingle()
        
        if self.level_type == 'normal':
            # Level sprite grouping
            if type(self.level_data) is dict:
                terrain_layer = import_csv(level_data['terrain'])
                self.terrain_sprites = self.create_tile_group(terrain_layer,'terrain')
                
                grass_layer = import_csv(level_data['grass'])
                self.grass_sprites = self.create_tile_group(grass_layer,'grass')
                
                crate_layer = import_csv(level_data['crates'])
                self.crate_sprites = self.create_tile_group(crate_layer,'crates')
                
                coin_layer = import_csv(level_data['coins'])
                self.coin_sprites = self.create_tile_group(coin_layer,'coins')
                
                fg_palm_layer = import_csv(level_data['fg palms'])
                self.fg_palm_sprites = self.create_tile_group(fg_palm_layer,'fg palms')
                
                bg_palm_layer = import_csv(level_data['bg palms'])
                self.bg_palm_sprites = self.create_tile_group(bg_palm_layer,'bg palms')
                
                enemy_layer = import_csv(level_data['enemies'])
                self.enemy_sprites = self.create_tile_group(enemy_layer,'enemies')
                
                constraint_layer = import_csv(level_data['constraints'])
                self.constraint_sprites = self.create_tile_group(constraint_layer,'constraints')
                
                self.tiles.add(self.terrain_sprites)
                
                # Decorative sprites
                self.decoration_tiles.add(self.grass_sprites)
                self.decoration_tiles.add(self.crate_sprites)
                self.decoration_tiles.add(self.fg_palm_sprites)
                self.decoration_tiles.add(self.bg_palm_sprites)
                
                # Interactive sprites
                self.coins = pygame.sprite.Group()
                self.coins.add(self.coin_sprites)
                
                self.enemies = pygame.sprite.Group()
                self.enemies.add(self.enemy_sprites)
                
                self.constraints = pygame.sprite.Group()
                self.constraints.add(self.constraint_sprites)
                
                # Player sprites
                player_layer = import_csv(level_data['player'])
                self.player_sprites = self.create_tile_group(player_layer,'player')
                
                # GUI sprites
                self.gui_sprite.add(GUISprite(self.gui, self.display_surface))
            else:
                print('Type of level data not supported for game mode')
                
        elif self.level_type == 'survival':
            if type(self.level_data) is list:
                self.fall_damage = 1
                self.generation_tiles = pygame.sprite.Group()
                self.build(self.level_data)
            else:
                print('Type of level data not supported for game mode')
        
        
    def create_tile_group(self,layer,layer_type):
        sprite = None
        if layer_type == 'player':
            sprite_group = pygame.sprite.GroupSingle()
        else:
            sprite_group = pygame.sprite.Group()
        for row_idx,row in enumerate(layer):
            for column_idx,column in enumerate(row):
                if column != '-1':
                    x = column_idx*TILE_SIZE
                    y = row_idx*TILE_SIZE
                    pos = (x,y)
                    
                    if layer_type == 'terrain':
                        terrain_tile_list = import_cut_tiles('Sprites/Terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(column)]
                        sprite = StaticTileSprite(pos, TILE_SIZE, tile_surface)                        
                        
                    if layer_type == 'grass':
                        grass_tile_list = import_cut_tiles('Sprites/Decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(column)]
                        sprite = StaticTileSprite(pos, TILE_SIZE, tile_surface)
                        
                    if layer_type == 'crates':
                        sprite = CrateSprite(pos, TILE_SIZE)
                                                                    
                    if layer_type == 'coins':
                        coin = Coin()
                        self.level_coins += coin.value
                        if column == '0': sprite = CoinSprite(coin, pos, TILE_SIZE, 'Sprites/Coins/gold')
                        else: sprite = CoinSprite(coin, pos, TILE_SIZE, 'Sprites/Coins/silver')                                           
                    
                    if layer_type == 'fg palms':
                        if column == '0': sprite = PalmSprite(pos, TILE_SIZE, 'Sprites/Terrain/palm_small', 38)
                        if column == '1': sprite = PalmSprite(pos, TILE_SIZE, 'Sprites/Terrain/palm_large', 64)
                        
                    if layer_type == 'bg palms':
                        sprite = PalmSprite(pos, TILE_SIZE, 'Sprites/Terrain/palm_bg', 38)
                        
                    if layer_type == 'enemies':
                        enemy = Enemy()
                        sprite = EnemySprite(enemy, pos, TILE_SIZE)
                    
                    if layer_type == 'constraints':
                        sprite = TileSprite(pos, TILE_SIZE)
                    
                    if layer_type == 'player':
                        if column == '0':
                            player = Player()
                            player.controls(pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_z, pygame.K_LSHIFT)
                            sprite = PlayerSprite(player, pos, self.display_surface)
                            gui = GUI(player, self)
                            self.player = player
                            self.player_init_pos = pos
                            self.gui = gui
                            
                    if sprite:
                        sprite_group.add(sprite)

        return sprite_group
                        
    #def create_jump_particles(self, pos):
    #    player_sprite = self.player_sprites.sprite
    #    player = player_sprite.player
        
    #    if player.to_right:
    #        pos -= pygame.math.Vector2(10.5)
    #    else:
    #        pos += pygame.math.Vector2(10,-5)
    #    jump_particle_sprite = ParticleEffect(pos, 'jump')
    #    self.dust_sprite.add(jump_particle_sprite)
            
    #def create_land_particles(self):
        #player_sprite = self.player_sprites.sprite
        #player = player_sprite.player
        
        #if not player.on_ground and player.on_ground and not self.dust_sprite.sprites():
            #if player.to_right:
            #    pos = pygame.math.Vector2(10.15)
            #else:
            #    pos = pygame.math.Vector2(-10,15)
            #fall_particle_sprite = ParticleEffect(player_sprite.rect.midbottom-pos,'land')
            #self.dust_sprite.add(fall_particle_sprite)
        
    #def get_player_on_ground(self):
    #   player_sprite = self.player_sprites.sprite
    #    player = player_sprite.player
        
    #    if player.on_ground:
    #        player.on_ground = True
    #    else:
    #        player.on_ground = False
        
    def build(self, layout):
        terrain_tile_list = import_cut_tiles('Sprites/Terrain/terrain_tiles.png')
        parsed_map = copy.deepcopy(layout)
        maximum_width = len(self.level_data[0])
        maximum_height = len(self.level_data)
        
        for row_idx,row in enumerate(layout):
            for column_idx,column in enumerate(row):
                x = column_idx*TILE_SIZE
                y = row_idx*TILE_SIZE
                pos = (x,y)
                # generation tile can be invisible not near platform
                # if terrain
                if column == 'X':
                    if column_idx == 0 or row[column_idx-1] == ' ':
                        tile_surface = terrain_tile_list[0]
                    elif column_idx == len(row)-1 or row[column_idx+1] == ' ':
                        tile_surface = terrain_tile_list[2]
                    elif (column_idx == 0 or row[column_idx-1] == ' ') and (column_idx == len(row)-1 or row[column_idx+1] == ' '):
                        tile_surface = terrain_tile_list[3]
                    else:
                        tile_surface = terrain_tile_list[1]
                    sprite = StaticTileSprite(pos, TILE_SIZE, tile_surface)
                    self.tiles.add(sprite)
                # if player
                elif column == 'P':
                    if not self.built:
                        player = Player()
                        player.controls(pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_z, pygame.K_LSHIFT)
                        player_sprite = PlayerSprite(player, pos, self.display_surface)
                        self.player_sprites.add(player_sprite)
                        self.player = player
                        self.player.x_vel = 8
                        self.player_init_pos = pos
                        self.start_time = pygame.time.get_ticks()
                    
        gui = GUI(self.player, self)
        gui_sprite = GUISprite(gui, self.display_surface)
        self.gui = gui
        self.gui_sprite.add(gui_sprite)
        
        self.built = True
        self.level_data = copy.deepcopy(parsed_map)
        
    def generate(self):
        maximum_width = len(self.level_data[0])
        maximum_height = len(self.level_data)
        gen_map = [[' ']*maximum_width for i in range(maximum_height)]
        generation_check_tile = int(len(self.level_data[0])/2)
        maximum_tiles_per_row = 5
        initial_row = 6
        fill_row = False
        for row_idx,row in enumerate(gen_map):
            generated_tile = 0
            fill_row = not fill_row
            for column_idx,column in enumerate(row):
                if column_idx == generation_check_tile:
                    obj = '|'
                    gen_map[row_idx][column_idx] = obj
                else:
                    if row_idx+1 >= initial_row and fill_row:
                        if generated_tile <= maximum_tiles_per_row:
                            obj = random.choice(level_objects)
                        else:
                            obj == ' '
                        if obj == 'X': 
                            generated_tile += 1
                        gen_map[row_idx][column_idx] = obj
            
        gen_array = np.array(gen_map)
        level_data_array = np.array(self.level_data)
        new_gen_map = np.concatenate((level_data_array, gen_array), axis = 1) 
        self.build(new_gen_map)
        
    def generate_column(self):
        maximum_width = len(self.level_data[0])
        maximum_height = len(self.level_data)
        gen_map = [[' '] for i in range(maximum_height)]
        maximum_tiles_per_column = 3
        initial_row = 6
        fill_row = False
        for row_idx,row in enumerate(gen_map):
            generated_tile = 0
            fill_row = not fill_row
            for column_idx,column in enumerate(row):
                if row_idx+1 >= initial_row and fill_row:
                    if generated_tile <= maximum_tiles_per_column:
                        obj = random.choice(level_objects)
                    else:
                        obj == ' '
                    if obj == 'X': 
                        generated_tile += 1
                    gen_map[row_idx][column_idx] = obj
            
        gen_array = np.array(gen_map)
        level_data_array = np.array(self.level_data)
        level_data_array = np.delete(level_data_array,0,1)
        new_gen_map = np.concatenate((level_data_array, gen_array), axis = 1) 
        self.build(new_gen_map)
        
    #def check_generation(self):
    #    player_sprite = self.player_sprites.sprite
    #    player = player_sprite.player
        
    #    generation_collision = pygame.sprite.spritecollide(player_sprite, self.generation_tiles, True)
        
    #    if generation_collision:
    #        self.generation_tiles.empty()
    #        self.generate()
                    
    def scroll_x(self):
        player_sprite = self.player_sprites.sprite
        player = player_sprite.player
        
        if player_sprite.rect.centerx < (SCREEN_WIDTH/4) and player.direction.x < 0:
            self.world_shift = 8
            player.x_vel = 0    
        elif player_sprite.rect.centerx > (SCREEN_WIDTH-(SCREEN_WIDTH/4)) and player.direction.x > 0:
            self.world_shift = -8
            player.x_vel = 0
        else:
            self.world_shift = 0
            player.x_vel = 8
            
        self.world_shifted += (-self.world_shift)
    
    def horizontal_movement_collision(self):
        player_sprite = self.player_sprites.sprite
        player = player_sprite.player
        player_sprite.rect.x += player.direction.x * player.x_vel
        
        #collision
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player_sprite.rect):
                if player.direction.x < 0:
                    player_sprite.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player_sprite.rect.left
                elif player.direction.x > 0:
                    player_sprite.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player_sprite.rect.right
        
        if player.on_left and (player_sprite.rect.left < self.current_x or player.direction.x >= 0):
                player.on_left = False
        if player.on_right and (player_sprite.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False
                
    def vertical_movement_collision(self):
        player_sprite = self.player_sprites.sprite
        player = player_sprite.player
        player_sprite.apply_gravity()
        
        #collision
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player_sprite.rect):
                if player.direction.y > 0:
                    player_sprite.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                    player.jumping = False
                elif player.direction.y < 0:
                    player_sprite.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
                    player.jumping = False
                    
        if player.on_ground and (player.direction.y < 0 or player.direction.y > player.gravity):
            player.on_ground = False
        #Avoid player spawning issue
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False
    
    def enemy_wall_collision(self):
        for sprite in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(sprite,self.constraint_sprites,False):
                sprite.enemy.reverse()
    
    def player_enemy_coin_collision(self):
        player_sprite = self.player_sprites.sprite
        player = player_sprite.player
        
        coin_collision = pygame.sprite.spritecollide(player_sprite, self.coins, True)
        #coin_collision = pygame.sprite.groupcollide(self.player_sprites, self.coins, False, True)
        
        if coin_collision:
            for coin in coin_collision:
                player.get_coin(coin.coin.value)
        # Alternative
        #    for collision in coin_collision:
        #        for coin in coin_collision[collision]:
        #            self.player.get_coin(coin.coin.value)
                
        
        enemy_collision = pygame.sprite.spritecollide(player_sprite, self.enemies, True)
        if enemy_collision:
            for enemy in enemy_collision:
                if player.attacking:
                    pass
                else:
                    player.get_hit(enemy.enemy.damage)
        
    def check_fall(self):
        player_sprite = self.player_sprites.sprite
        player = player_sprite.player
        
        if player_sprite.rect.top > SCREEN_HEIGHT:
            self.player.get_hit(self.fall_damage)
            
            # Reset player to init pos aswell as eventual world shift
            player_sprite.rect = player_sprite.image.get_rect(topleft = self.player_init_pos)
            self.world_shift = self.world_shifted
            self.world_shifted = 0
            
    def won(self):
        end_screen_sprite = WinLoseSprite('YOU WON!', self.display_surface)
        self.end_screen.add(end_screen_sprite)
        self.win = True
        
    def lost(self):
        end_screen_sprite = WinLoseSprite('GAME OVER', self.display_surface)
        self.end_screen.add(end_screen_sprite)
        self.win = False
                
    def run(self):
        if self.win is None:
            # Time elapsed in seconds
            self.current_time = (pygame.time.get_ticks()-self.start_time)/1000
            
            
            # dust particles
            self.dust_sprite.update(self.world_shift)
            self.dust_sprite.draw(self.display_surface)
            
            #Level tiles
            self.decoration_tiles.update(self.world_shift)
            self.decoration_tiles.draw(self.display_surface)
            
            if self.level_type == 'normal':
                self.coins.update(self.world_shift)
                self.coins.draw(self.display_surface)
                
                self.enemies.update(self.world_shift)
                self.constraints.update(self.world_shift)
                self.enemy_wall_collision()
                self.enemies.draw(self.display_surface)
                
            if self.level_type == 'survival':
                #self.survival_shift -= self.current_time*0.05
                self.generation_tiles.update(self.survival_shift)
                self.generation_tiles.draw(self.display_surface)
                self.tiles.update(self.survival_shift)
            else:
                self.tiles.update(self.world_shift)    
            
            self.tiles.draw(self.display_surface)
            
            # Player
            self.player_sprites.update()
            self.horizontal_movement_collision()
            #self.get_player_on_ground() 
            self.vertical_movement_collision()
            #self.create_land_particles()
            if self.level_type == 'normal':
                self.scroll_x()
            self.player_sprites.draw(self.display_surface)
            
            # GUI
            self.gui_sprite.update()
            self.gui_sprite.draw(self.display_surface)
            
            if self.level_type == "normal":
                self.player_enemy_coin_collision()
            
            self.check_fall()
            
            if self.level_type == "survival":
                self.world_shifted += 1 #self.current_time*0.05
                if int(self.world_shifted/TILE_SIZE) >= 1:
                    self.world_shifted = 0
                    self.generate_column()
                #self.check_generation()
        else:
            self.end_screen.update()
            
        