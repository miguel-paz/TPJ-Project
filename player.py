import pygame
import logging

from command import Actor, Left, Right, Jump, Attack, Dash, Stop
from subject import Subject, EVENT_COIN_ACQUIRED, EVENT_PLAYER_INJURED

class Player(Actor, Subject):
    def __init__(self):
        Subject.__init__(self)
        
        self.control_keys = dict()
                
        #player movement
        self.gravity = 0.8
        self.gravity_wall = self.gravity/2.5
        self.direction = pygame.math.Vector2(0,0)
        self.x_vel = 3
        self.y_vel = -16
        self.y_inc = self.y_vel/1000
        self.y_inc_temp = self.y_inc
        
        self.right_disable = False
        self.left_disable = False
        
        #player status
        self.max_health = 100
        self.status = 'idle'
        self.jumping = False
        self.to_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.attacking = False
        self.dead = False
        
        #abilities
        self.dash_speed = self.x_vel*2
        self.dash_cooldown = 1000        
        self.dash_input = 0
        self.attack_cooldown = 1000
        self.attack_input = 0
        
        self.abilities = {'attack': [self.attack_input,self.attack_cooldown], 'dash': [self.dash_input,self.dash_cooldown]}
        
    
    def controls(self, left, right, jump, attack, dash):
        self.control_keys = {left: Left, right: Right, jump: Jump, attack: Attack, dash: Dash}        
    
    def command(self, control):
        if control == "Stop":
            cmd = Stop()
            cmd.execute(self)
            return cmd
        else:
            for key in self.control_keys.keys():
                if control[key]:
                    if self.control_keys[key].__name__ == "Jump" and self.jumping:
                        return
                    else:
                        print("Sending " + self.control_keys[key].__name__ )
                        cmd = self.control_keys[key]()
                        cmd.execute(self)
            return
        print("Invalid key")
        
    def move(self, movement):
    
        if movement == "Right":
            self.direction.x = 1
            self.to_right = True
        elif movement == "Left":
            self.direction.x = -1
            self.to_right = False
        
        if movement == "Stop":
            self.direction.x = 0
        
        if movement == "Jump": 
            if self.on_ground:
                self.direction.y = self.y_vel
                
        if movement == "Attack":
            self.attack()
                
        if movement == "Dash":
            self.dash()
        
    def jump(self,wall=False):
        self.direction.y = max(self.direction.y+self.y_inc_temp,self.y_vel)
        print('Max: ' + str(self.direction.y))
    
    def attack(self):
        current_time = pygame.time.get_ticks()
        if self.check_cooldown('attack', current_time) and not self.attacking:
            self.attacking = True
            self.abilities['attack'][0] = current_time
        else: 
            print('attack on cooldown')
    
    def dash(self):
        current_time = pygame.time.get_ticks()
        if self.check_cooldown('dash', current_time):
            if self.to_right:
                self.direction.x = self.dash_speed
            else:
                self.direction.x = -self.dash_speed
            
            self.abilities['dash'][0] = current_time
        else: 
            print('dash on cooldown')
            if self.on_ground:
                self.direction.x = 0
                
    
    def check_cooldown(self,ability,current_time):
        input_time = self.abilities[ability][0]
        cooldown = self.abilities[ability][1]
        if (current_time - input_time) >= cooldown:
            return True
        return False
         
    def get_status(self):
        if self.attacking:
            self.status = "attack"
        elif self.direction.y < 0:    
            self.status = 'jump'
        elif self.direction.y > self.gravity:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'
        
    
    def get_hit(self, damage):
        self.damage_taken = self.max_health*damage
        self.notify(EVENT_PLAYER_INJURED)
        
    def get_coin(self, value):
        self.acquired_coin_value = value
        self.notify(EVENT_COIN_ACQUIRED)
    
    def kill(self):
        logging.info("Player has died")
        self.dead = True
            