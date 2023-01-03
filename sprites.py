import pygame

from player import Player
from enemy import Enemy
from support import import_folder
from coin import Coin
from gui import GUI
from button import Button

class TileSprite(pygame.sprite.Sprite):
    def __init__(self,pos,size):
        super().__init__()
        self.image = pygame.Surface((size,size))
        self.rect = self.image.get_rect(topleft = pos)
        self.image.fill('red')
        
    def update(self, x_shift):
        self.rect.x += x_shift
        
class StaticTileSprite(TileSprite):
    def __init__(self,pos,size,surface):
        super().__init__(pos,size)
        self.image = surface
        
class CrateSprite(StaticTileSprite):
    def __init__(self,pos,size):
        super().__init__(pos,size,pygame.image.load('Sprites/Terrain/crate.png').convert_alpha())
        offset_pos = (pos[0], size + pos[1])
        self.rect = self.image.get_rect(bottomleft = offset_pos)
        
class AnimatedTileSprite(TileSprite):
    def __init__(self,pos,size,path):
        super().__init__(pos,size)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0 

        image = self.frames[int(self.frame_index)]
            
        self.image = image 

    def update(self, x_shift):
        self.rect.x += x_shift
        self.animate()
        
class CoinSprite(AnimatedTileSprite):
    def __init__(self, coin: Coin, pos,size,path):
        super().__init__(pos,size,path)
        self.coin = coin
        centered_pos = (pos[0]+(size/2),pos[1]+(size/2))
        self.rect = self.image.get_rect(center = centered_pos)
        
class PalmSprite(AnimatedTileSprite):
    def __init__(self,pos,size,path,offset):
        super().__init__(pos,size,path)
        offset_pos = (pos[0], pos[1] - offset)
        self.rect.topleft = offset_pos
                
class EnemySprite(AnimatedTileSprite):
    def __init__(self, enemy: Enemy, pos, size):
        super().__init__(pos,size,'Sprites/Enemy/run')
        
        self.enemy = enemy
        
        self.rect.y += size - self.image.get_height()

    def update(self, x_shift):
        def move():
            self.rect.x += self.enemy.speed
    
        self.rect.x += x_shift
        self.animate()
        move()
        if self.enemy.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)

class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, player: Player, pos, surface):
        super().__init__()

        self.player = player
        
        # Player animation params
        player_path = 'Sprites/Character/'
        self.animations = {'idle':[], 'run':[], 'jump':[], 'fall':[], 'attack':[]}
        for animation in self.animations.keys():
                full_path = player_path + animation
                self.animations[animation] = import_folder(full_path)
                
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

        self.prev_animation = None
        self.wait = False        

        #dust particles
        self.dust_run_particles = import_folder('Sprites/Character/dust_particles/run')
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.15
        self.display_surface = surface
    
    def apply_gravity(self):
        gravity = self.player.gravity
        self.player.direction.y += self.player.gravity
        self.rect.y += self.player.direction.y
    
    def update(self):    
        
        def animate():
            
            #print(self.player.status)
            animation = self.animations[self.player.status]
            
            if self.player.attacking:
                self.wait = True
                self.prev_animation = self.animations['attack']
                
            if self.wait:
                animation = self.prev_animation
                #self.frame_index += self.animation_speed/3
        
            self.frame_index += self.animation_speed
           
            if self.frame_index >= len(animation):
                self.frame_index = 0
                if self.wait:
                    self.wait = False
                    self.player.attacking = False

            #if self.wait: image = animation[0]
            image = animation[int(self.frame_index)]
            
            if not self.player.to_right:
                image = pygame.transform.flip(image,True,False)
            
            self.image = image
            
            #set the rectangle
            if self.player.on_ground:
                if self.player.on_right:
                    self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
                elif self.player.on_left:
                    self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
                else:
                    self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            elif self.player.on_ceiling:
                if self.player.on_right:
                    self.rect = self.image.get_rect(topright=self.rect.topright)
                elif self.player.on_left:
                    self.rect = self.image.get_rect(topleft=self.rect.topleft)
                else:
                    self.rect = self.image.get_rect(midtop=self.rect.midtop)
                    
            self.player.rect = self.rect
            
            #elif self.on_ceiling:
            #    self.rect = self.image.get_rect(midtop=self.rect.midtop)
            #else:
            #    self.rect = self.image.get_rect(center=self.rect.center)
            
            #if self.on_ground:
            #    self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            #elif self.on_ceiling:
            #    self.rect = self.image.get_rect(midtop=self.rect.midtop)
            #else:
            #    self.rect = self.image.get_rect(center=self.rect.center)
        
        def run_dust_animation():
            if self.player.status == 'run' and self.player.on_ground:
                self.dust_frame_index += self.dust_animation_speed
                if self.dust_frame_index >= len(self.dust_run_particles):
                    self.dust_frame_index = 0
                    
                dust_particle = self.dust_run_particles[int(self.dust_frame_index)]
                
                offset = pygame.math.Vector2(6,9)
                
                pos = self.rect.bottomleft
                if not self.player.to_right:
                    pos = self.rect.bottomright
                    #flipped dust particle
                    dust_particle = pygame.transform.flip(dust_particle,True,False)
                self.display_surface.blit(dust_particle,pos-offset)
    
        self.player.get_status()
        animate()
        run_dust_animation()
        
        
class GUISprite(pygame.sprite.Sprite):
    def __init__(self, gui: GUI, surface):
        super().__init__()
        
        self.gui = gui
        self.image = surface
        self.rect = self.image.get_rect()
        
        self.font = pygame.font.Font('Sprites/Ui/ARCADEPI.TTF', 25)
        
        if self.gui.level.level_type == 'normal':
            self.health_bar = pygame.image.load('Sprites/Ui/health_bar.png')
            self.health_bar_pos = (20,10)
            self.health_bar_begin = (54,39)
            self.health_bar_width = 152
            self.health_bar_height = 4
            
            self.coin = pygame.image.load('Sprites/Ui/coin.png')        
            self.coin_rect = self.coin.get_rect(topleft = (self.health_bar_pos[0], self.health_bar_pos[1]+self.coin.get_height()+20))
        
    def update(self):
        if self.gui.level.level_type == 'normal':
            self.image.blit(self.health_bar, self.health_bar_pos)
            health_ratio = self.gui.player_current_health / self.gui.player_max_health
            health_bar_size = self.health_bar_width * health_ratio
            health_bar_rect = pygame.Rect(self.health_bar_begin, (health_bar_size,self.health_bar_height))
            pygame.draw.rect(self.image, 'red', health_bar_rect)
            
            self.image.blit(self.coin, self.coin_rect)
            coin_amount = self.font.render(f"{self.gui.player_coins}/{self.gui.level.level_coins}", False, "black")
            coin_amount_rect = coin_amount.get_rect(midleft = (self.coin_rect[0]+40,self.coin_rect.centery))
            self.image.blit(coin_amount, coin_amount_rect)
            
        if self.gui.level.level_type == 'survival':
            text = self.font.render(f'{self.gui.level.current_time}', False, "black")
            text_rect = text.get_rect(topleft = (20,10))
            self.image.blit(text, text_rect)
        
class TitleSprite(pygame.sprite.Sprite):
    def __init__(self, text, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font('Sprites/Ui/ARCADEPI.TTF', 65)
        self.text = self.font.render(text, False, "white")
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (self.image.get_width()/2, self.image.get_height()/2)
        offset = 160
        self.text_rect.centery -= offset 
        
        #self.font_shadow = pygame.font.Font('Overworld/graphics/ui/ARCADEPI.TTF', 68)
        self.font_shadow = pygame.font.Font('Sprites/Ui/ARCADEPI.TTF', 65)
        self.text_shadow = self.font_shadow.render(text, False, "black")
        self.text_shadow_rect = self.text_shadow.get_rect()
        self.text_shadow_rect.center = self.text_rect.center
        self.text_shadow_rect.centery = self.text_rect.centery + 7
        
        
    def update(self):
        self.image.blit(self.text_shadow, self.text_shadow_rect)
        self.image.blit(self.text, self.text_rect)

class ButtonSprite(pygame.sprite.Sprite):
    def __init__(self, button: Button, text, offset, surface):
        super().__init__()
        self.button = button
        button_width = 100
        button_height = 50
        self.image = surface
        self.rect = pygame.Rect((20,20), (button_width,button_height))

        self.font = pygame.font.Font('Sprites/Ui/ARCADEPI.TTF', 25)
        self.text = self.font.render(text, False, "white")
        self.text_rect = self.text.get_rect()
        
        self.rect.width = self.text_rect.width + 30
        self.rect.center = (self.image.get_width()/2, self.image.get_height()/2)
        if offset[0] != 0:
            self.rect.y += (button_height*offset[0]) + (offset[0]*offset[1])  
        self.text_rect.center = self.rect.center
        
    def update(self):
        pygame.draw.rect(self.image, 'black', self.rect)
        self.image.blit(self.text, self.text_rect)
        
class WinLoseSprite(pygame.sprite.Sprite):
    def __init__(self, text, surface):
        super().__init__()
        self.image = surface
        self.font = pygame.font.Font('Sprites/Ui/ARCADEPI.TTF', 65)
        self.text = self.font.render(text, False, "white")
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (self.image.get_width()/2, self.image.get_height()/2)
        self.rect = self.image.get_rect()
        #self.font_shadow = pygame.font.Font('Overworld/graphics/ui/ARCADEPI.TTF', 68)
        self.font_shadow = pygame.font.Font('Sprites/Ui/ARCADEPI.TTF', 65)
        self.text_shadow = self.font_shadow.render(text, False, "black")
        self.text_shadow_rect = self.text_shadow.get_rect()
        self.text_shadow_rect.center = self.text_rect.center
        self.text_shadow_rect.centery = self.text_rect.centery + 7
        
        
    def update(self):
        self.image.fill('grey')
        self.image.blit(self.text_shadow, self.text_shadow_rect)
        self.image.blit(self.text, self.text_rect)
        

        